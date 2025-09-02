# -*- coding: utf-8 -*-
import json
import logging as logger
import os

import pandas as pd

from .add_limit_builder import AddLimitPartBuilder, Director
from .limit_text_parser import LimitProcessingFields
from .settings import to_rename_input

# # # # История изменений: # # # #
# 13.11.2020 - Файл создан.
# 26.11.2020 - Доработана функция correct_znac (возможность парсить дополнительные строки с "<") +
#               + добавлена вязкость 40 для обработки
# 29.12.2020 - добавлена функция чтения лимитов из json из БД.
# 12.01.2021 - Обработка файла лимитов приведена в ОО формат
# 05.02.2021 - Доработка по гибкому набору параметров
# # # # # # # # # # # # # # # # # #

# Класс входных лимитов
class InputLimit(object):
    def __init__(self, limit_path, _format_):
        self.path = limit_path
        self.format = _format_
        assert self.format in ['json', 'excel', 'dictionary'], 'Input limit format is wrong!'
        if self.format == 'excel':
            self.data = self.read_excel()
        elif self.format == 'json':
            self.data = self.read_json()
        elif self.format == 'dictionary':
            self.data = self.read_dictionary()

    def read_excel(self):
        return pd.read_excel(self.path).iloc[:, [0, 1, 34]]

    def read_json(self):
        with open(self.path, 'r', encoding='utf-8') as handle:
            limit = json.loads(handle.read())
        return limit

    def read_dictionary(self):
        return self.path


# Класс-адаптер для входных лимитов, делающий из входного формата нужный датафрейм
class AdapterInput2LimitDF(InputLimit):
    def __init__(self, limit_path, _format_):
        super().__init__(limit_path, _format_)
        if self.format == 'excel':
            self.DF = self.excel_transform()
        elif self.format == 'json':
            self.DF = self.json_transform()
        elif self.format == 'dictionary':
            self.DF = self.dict_transform()

    def excel_transform(self):
        df_limit = self.data
        df_limit.columns = ['Показатель', 'Описание', 'Значение']
        df_limit.dropna(subset=['Значение'], inplace=True)

        df_limit['lambda'] = df_limit['Значение'].apply(self.correct_sign)
        df_limit['Описание'] = df_limit['Описание'].str.lower()

        to_replace = {
            'вязкость при 100℃ sae 40': 'кинематическая вязкость при 100 °с',
            'вязкость при 40℃ sae 40': 'кинематическая вязкость при 40 °с',
            'содержание воды (акватест)': 'вода',
            'топливо': 'содержание горючего',
            'гликоль': 'содержание гликоля',
            'степень нитрования': 'продукты нитрификации',
        }

        df_limit.replace(to_replace=to_replace, inplace=True)

        return df_limit

    def json_transform(self):
        def make_string_limit(x: list):
            return '{0} {1}'.format(
                ('' if pd.isna(x[0]) else '<' + str(x[0])), ('' if pd.isna(x[1]) else '>' + str(x[1]))
            )

        limit = self.data
        df_limit = pd.DataFrame()
        df_limit['Показатель'] = limit.keys()
        df_limit['Описание'] = df_limit['Показатель'].replace(to_rename)
        df_limit['Значение'] = pd.Series(limit.values()).apply(make_string_limit)

        df_limit['lambda'] = df_limit['Значение'].apply(self.correct_sign)
        df_limit['Описание'] = df_limit['Описание'].apply(lambda x: x.lower().rsplit(' (')[0])

        return df_limit

    def dict_transform(self):
        df_limit = pd.DataFrame()
        limit = self.data

        df_limit['Показатель'] = limit.keys()
        df_limit['Описание'] = df_limit['Показатель'].replace(to_rename_input)
        df_limit['Значение'] = pd.Series(limit.values())
        # df_limit['lambda'] = df_limit['Значение'].apply(self.correct_sign)
        df_limit['lambda'] = df_limit['Значение'].apply(lambda x: LimitProcessingFields(x, {}))

        df_limit['Описание'] = df_limit['Описание'].apply(lambda x: x.lower().rsplit(' (')[0])

        return df_limit

    @staticmethod
    def correct_sign(x):
        """
        Преобразования выражения вида N1<x<N2 в функции сравнения
        """

        def kv100(x, minn, maxx):
            if x < minn:
                return -1
            elif x > maxx:
                return 1
            else:
                return 0

        if ('<' in x) and ('>' in x):
            strs = x.split(';')
            return lambda x: kv100(
                x, float(strs[0].replace('<', '').replace(',', '.')), float(strs[-1].replace('>', '').replace(',', '.'))
            )
        elif '>' in x:
            strs = x.split('>')[-1].split(' ')[0]
            strs = strs if type(strs) == str else strs[0]
            return lambda x: x > float(strs)
        elif '<' in x:
            strs = x.split('<')[-1].split(' ')[0]
            strs = strs if type(strs) == str else strs[0]
            return lambda x: -1 if x < float(strs) else 0


class AlgInterpretation:
    def __init__(self, globClass, df_select, alg_df, limit_path):
        self.operation_time_limit = 25000
        self.globClass = globClass

        self.df_select = df_select
        logger.info('Sample data loaded successfully')
        logger.info('Sample data: {}'.format(self.df_select))

        self.alg = self.read_alg(alg_df)

        if isinstance(limit_path, dict):
            logger.info('limits from dict')
            self.df_limit = AdapterInput2LimitDF(limit_path=limit_path, _format_='dictionary').DF
        elif os.path.splitext(limit_path)[1] == '.xlsx':
            logger.info('limits from xlsx!')
            self.df_limit = AdapterInput2LimitDF(limit_path=limit_path, _format_='excel').DF
        elif os.path.splitext(limit_path)[1] == '.json':
            logger.info('limits from json!')
            self.df_limit = AdapterInput2LimitDF(limit_path=limit_path, _format_='json').DF

        logger.info('Limits loaded successfully')
        logger.info('Limits: {}'.format(self.df_limit))

        self.add_limits()
        self.check_for_alg()

        logger.info('Algorithm loaded successfully')
        logger.info('Algorithm: {}'.format(self.alg))

    @staticmethod
    def read_alg(alg_df):
        """
        Метод:
        1) считывает алгоритм интепретации*
        2) приводит к единообразию название параметров
        3) преобразует выражения (снижения, повышения, норма) в числовые значения

        *временно убирает, подсвеченные желтым правила
        """

        alg = alg_df.copy()   # pd.read_excel(file_path, sheet_name='algorithm',engine='openpyxl').iloc[:, :10]
        # В данном куске нет необходимости. т.к. все вероятности заполнены
        # alg['Вероятность2(+)'] = alg['Вероятность2(+)'].fillna(1)
        # alg['Вероятность2(-)'] = alg['Вероятность2(-)'].fillna(1)

        for param in ['№ п/п', 'Проверяемый параметр', 'нарушение', 'Причина', 'Вероятность1', 'вторичный показатель']:
            index_all = alg.loc[alg.loc[:, param].notna(), param].index
            for prev_i, next_i in zip(index_all, index_all[1:]):
                alg.loc[prev_i : next_i - 1, param] = alg.loc[prev_i, param]

            alg.loc[next_i:, param] = alg.loc[next_i, param]

        alg['Проверяемый параметр'] = alg['Проверяемый параметр'].str.lower()
        alg['вторичный показатель'] = alg['вторичный показатель'].str.lower()

        # В данном куске нет необходимости т.к. Столбец Результат всегда пустой
        # alg.loc[alg[(alg['Результат'] == 'причина возможна') & (alg['Вероятность2'] == 1)].index, 'Вероятность2'] = 0

        to_replace = {
            'ниже нормы': 0,
            'выше нормы': 1,
        }
        # 'изменен': 2,
        # 'в лимите': 0}

        to_replace_2 = {
            'кв40': 'кинематическая вязкость при 40 °с',
            'кв 40': 'кинематическая вязкость при 40 °с',
            'кв 100': 'кинематическая вязкость при 100°C',
            'кч': 'кислотное число',
            'давление масла p2': 'давление масла p2',
            'давление масла p3': 'давление масла p3',
            'давление масла p1': 'давление масла p1',
            'воду': 'вода',
            'сажу': 'сажа',
            'уровень сажи': 'сажа',
            'ик "нитрование"': 'продукты нитрификации',
            'ик "топливо"': 'содержание горючего',
            'гликоль': 'содержание гликоля',
            'степень нитрования': 'продукты нитрификации',
            'температуру вспышки': 'температура вспышки',
            'наработку масла': 'наработка масла',
            'общую наработку': 'общая наработка',
            'сажу в динамике': 'сажа в динамике',
        }

        alg.replace(to_replace=to_replace, inplace=True)

        alg['вторичный показатель'] = alg['вторичный показатель'].str.replace('проверить ', '')

        alg.replace(to_replace=to_replace_2, inplace=True)

        return alg

    def add_limits(self):
        """
        Проверка лимитов, которые зависят от начальных значений показателя масел (присадками):
        """
        limit_auto_builder = Director(self.globClass, list(self.df_select.columns))
        builder = AddLimitPartBuilder(value_dataframe=self.df_select, limits_dataframe=self.df_limit)
        limit_auto_builder.builder = builder
        limit_auto_builder.build_limits()
        self.excepted_fields = set(limit_auto_builder.excepted_fields)
        self.checked_fields = set(limit_auto_builder.checked_fields)

    @staticmethod
    def test(x, low, high):
        """
        функция сравнения
        :param x: значение
        :param low: верхний лимит
        :param high: нижний лимит
        """
        if x < low:
            return -1
        elif x > high:
            return 1
        else:
            return 0

    @staticmethod
    def convert_to_text(x):
        """
        обратная ковертация из мат. в выражения
        :param x: - число
        """
        if x == 2:
            return 'норма'
        elif x == 1:
            return 'превышен'
        elif x == 0:
            return 'снижен'

    def get_limits(self):
        return self.df_limit['Описание'].unique()

    def get_df_limits(self):
        return self.df_limit

    def get_df(self):
        return self.df_select

    def get_check_property(self):
        return self.df_limit['Описание'].values

    def check_for_alg(self):
        """
        Метод проверки нарушений лимитов и свойств масел.
        """
        upper_test = self.alg[['Проверяемый параметр', 'нарушение']].drop_duplicates()
        self.alg['KEY'] = self.alg['Проверяемый параметр'] + '|' + self.alg['нарушение'].astype(str)
        for sur_i in upper_test.iterrows():
            alg_row = sur_i[1]
            if self.df_select.get('check_' + alg_row['Проверяемый параметр']) is None:
                logger.info(f'пропущено при сравнении: {"check_" + alg_row["Проверяемый параметр"]}')
                continue
            tb = self.df_select[self.df_select['check_' + alg_row['Проверяемый параметр']] == alg_row['нарушение']]
            print('######' * 20)
            print(tb)

            if not tb.empty:
                alg_select_all = self.alg[self.alg['Проверяемый параметр'] == alg_row['Проверяемый параметр']]
                alg_select_all = alg_select_all[alg_select_all['нарушение'] == alg_row['нарушение']]
                # этот цикл проставляет маркеры для строк, которые должны пойти в result
                for tb_row in tb.iterrows():
                    row = tb_row[1]
                    for_marker = list(set(alg_select_all['KEY'].values))
                    ind = self.alg[
                        (self.alg['Проверяемый параметр'] == alg_row['Проверяемый параметр'])
                        & (self.alg['KEY'].isin(for_marker))
                    ].index
                    col_name = str(int(row['номер пробы']))
                    self.alg.loc[ind, f'marker_{col_name}'] = 1

                for row_i in alg_select_all.iterrows():
                    alg_row_i = row_i[1]

                    if self.df_select.get('check_' + alg_row_i['вторичный показатель']) is None:
                        logger.info(f'пропущено при сравнении №2: {"check_" + alg_row_i["вторичный показатель"]}')
                        continue

                    if alg_row_i['Вероятность1'] == 1:
                        compare_value = alg_row_i['нарушение'] if isinstance(alg_row_i['нарушение'], int) else 666
                        res = tb[tb['check_' + alg_row_i['Проверяемый параметр']] == compare_value]
                    else:
                        compare_value = alg_row_i['нарушение.1'] if isinstance(alg_row_i['нарушение.1'], int) else 666
                        res = tb[tb['check_' + alg_row_i['вторичный показатель']] == compare_value]

                    if not res.empty:
                        for row_ii in res.iterrows():
                            col_name = str(int(row_ii[1]['номер пробы']))
                            self.alg.loc[row_i[0], f'{col_name}'] = 1
                            if alg_row_i['Вероятность1'] == 1:
                                self.alg.loc[row_i[0], 'вторичный показатель'] = ' '

        self.alg.drop(columns=['KEY'], inplace=True)
