# -*- coding: utf-8 -*-
import logging as logger

import numpy as np
import pandas as pd
from tabulate import tabulate

from .alg_interpretation import AlgInterpretation
from .settings import *

# # # # История изменений: # # # #
# 13.11.2020 - Файл создан.
# 26.11.2020 - Добавлен 3й слой обработки результата + последующий вывод
# 25.12.2020 - Скорректирована функция transform_input_json(добавлено удаление дополнительных строковых полей из
# входных данных
# 13.01.2021 - Вычисление результатов оформленов в объектный формат
#
#
# # # # # # # # # # # # # # # # # #


class InputData(object):
    def __init__(self, input_json):
        self.input_json = input_json
        self.init_features, self.df_select = self.transform_input_json()
        logger.info('Json parsed successfully')

    def transform_input_json(self):
        df = pd.DataFrame(self.input_json).reset_index(drop=True)
        list_deff = list(set(df.columns) - set(string_fields) - set(parameter_list_not_interp))
        df = df[list_deff]
        llist = []
        for i in df.columns:
            if type(to_rename_input.get(i)) == type(None):
                logger.error(f'Нет соответсвий для  {i}')
                llist.append(i)
            else:
                llist.append(to_rename_input.get(i).lower().rsplit(' (')[0])
        df.columns = llist
        df['номер пробы'] = df.index + 1
        init_svoistv = df.head(1)
        df_select = df.tail(1)
        return init_svoistv, df_select


class InterpretationResult(object):
    def __init__(self, globClass, input_data, alg_df, limit_path):
        self.globClass = globClass
        self.alg_int = AlgInterpretation(self.globClass, input_data.df_select, alg_df, limit_path)
        self.output_for_xls, self.aggr_res_dict = self.aggregate_result()
        self.output_for_json = self.make_output_dict()
        self.string_output = self.get_string_output()
        logger.info('Result calculated successfully')
        logger.info('Result: {}'.format(self.output_for_json))
        logger.info('Result string: {}'.format(self.string_output))

    def aggregate_result(self):
        num = str(self.alg_int.df_select['номер пробы'].iloc[-1])
        pre_output = pd.DataFrame(
            columns=[
                'Выявлено нарушение',
                'Пров.показатель',
                'отклонение',
                'Причиной является',
                'Причина',
                'Итоговая вероятность',
                'Что подтверждает',
                'Втор.показатель',
            ]
        )
        # делаем проверку, что если результат не None, тогда записываем результаты
        if self.alg_int.alg.get('marker_' + num) is not None:

            self.alg_int.alg.loc[:, 'key'] = (
                self.alg_int.alg.loc[:, 'Проверяемый параметр']
                + self.alg_int.alg.loc[:, 'нарушение'].astype(str)
                + self.alg_int.alg.loc[:, 'Причина']
            )
            result = self.alg_int.alg.copy().loc[
                (self.alg_int.alg.loc[:, 'key']).isin(
                    self.alg_int.alg.loc[self.alg_int.alg.loc[:, 'marker_' + num].notna(), 'key']
                )
            ]

            if result.get(num) is None:
                result.loc[:, num] = 0

            result.drop(columns=['key'], inplace=True)
            result.loc[:, num].fillna(0, inplace=True)
            result.loc[:, 'Результат'] = result.loc[:, num].copy().replace({0: 'Не выявлено', 1: 'Подтверждено'})
            result.loc[:, 'нарушение'] = result.loc[:, 'нарушение'].apply(lambda x: self.alg_int.convert_to_text(x))
            result.loc[:, 'нарушение.1'] = (
                result.loc[:, 'нарушение.1'].apply(lambda x: self.alg_int.convert_to_text(x)).fillna(' ')
            )

            logger.info('Pre-result calculated successfully')
            logger.info('Pre-result: {}'.format(tabulate(result, headers=result.columns)))
            print(tabulate(result, headers=result.columns))

            z = (
                result.groupby(['Проверяемый параметр', 'нарушение', 'Причина'], as_index=False)
                .apply(lambda x: transform_to_need_format(x, num))
                .sort_values(['Проверяемый параметр', 'Вероятность'], ascending=False)
            )

            for i in result.iterrows():
                if not i[1]['Проверяемый параметр'] in self.globClass.datawarning:
                    self.globClass.datawarning[i[1]['Проверяемый параметр']] = [i[1]['нарушение']]
                else:
                    if not i[1]['нарушение'] in self.globClass.datawarning[i[1]['Проверяемый параметр']]:
                        self.globClass.datawarning[i[1]['Проверяемый параметр']].append(i[1]['нарушение'])

            # проверка есть ли 100% подтверждение причины. (вариация в выводе)
            validate_100 = z[z['Вероятность'] > probability_limit]

            if not validate_100.empty:

                for i in range(len(validate_100)):
                    res = validate_100.iloc[i]
                    zz = [
                        'Выявлено нарушение:',
                        res['Проверяемый параметр'],
                        res['нарушение'],
                        'Причиной является:',
                        res['Причина'],
                        1 if res['Вероятность'] > 1 else res['Вероятность'],
                        'Что подтверждает:',
                        res['вторичный показатель'],
                    ]

                    pre_output = pd.concat(
                        (
                            pre_output,
                            pd.DataFrame(
                                np.array(zz).reshape(1, len(zz)),
                                columns=[
                                    'Выявлено нарушение',
                                    'Пров.показатель',
                                    'отклонение',
                                    'Причиной является',
                                    'Причина',
                                    'Итоговая вероятность',
                                    'Что подтверждает',
                                    'Втор.показатель',
                                ],
                            ),
                        )
                    ).reset_index(drop=True)
                df3 = self.layer3(validate_100)

                aggr_res = {
                    'deviation': [
                        ';'.join(list(set(i.split(';'))))
                        for i in df3[df3['Вероятность'] == df3['Вероятность'].max()]['Параметр'].to_list()
                    ],
                    'reason': df3[df3['Вероятность'].max() == df3['Вероятность']]['Причина'].to_list(),
                    'probability': df3[df3['Вероятность'] == df3['Вероятность'].max()]['Вероятность'].to_list(),
                }
            else:
                zz = [
                    '-',
                    '-',
                    'Не выявлено нарушений, по вероятности превышающих нижний предел',
                    '-',
                    '-',
                    '-',
                    '-',
                    '-',
                ]
                pre_output = pd.concat(
                    (
                        pre_output,
                        pd.DataFrame(
                            np.array(zz).reshape(1, len(zz)),
                            columns=[
                                'Выявлено нарушение',
                                'Пров.показатель',
                                'отклонение',
                                'Причиной является',
                                'Причина',
                                'Итоговая вероятность',
                                'Что подтверждает',
                                'Втор.показатель',
                            ],
                        ),
                    )
                ).reset_index(drop=True)
                aggr_res = {
                    'deviation': 'Не выявлено нарушений, по вероятности превышающих нижний предел',
                    'reason': '-',
                    'probability': '-',
                }
        else:
            zz = ['-', '-', 'Превышения допустимых пределов не выявлено', '-', '-', '-', '-', '-']
            pre_output = pd.concat(
                (
                    pre_output,
                    pd.DataFrame(
                        np.array(zz).reshape(1, len(zz)),
                        columns=[
                            'Выявлено нарушение',
                            'Пров.показатель',
                            'отклонение',
                            'Причиной является',
                            'Причина',
                            'Итоговая вероятность',
                            'Что подтверждает',
                            'Втор.показатель',
                        ],
                    ),
                )
            ).reset_index(drop=True)
            aggr_res = {'deviation': 'Превышения допустимых пределов не выявлено', 'reason': '-', 'probability': '-'}
        output = pre_output.to_dict(orient='list')

        return output, aggr_res

    def layer3(self, validate):
        names = self.alg_int.df_select.columns
        # Формируем dataframe для результата
        resdf = pd.DataFrame(columns=['Причина', 'Вероятность', 'Параметр'])
        # Набор уникальных поричин с параметрами вызвавших их
        cases = {}
        for i_case in validate.iloc:
            p1 = i_case['Проверяемый параметр'] + '-' + i_case['нарушение']
            prop = i_case['Вероятность']

            llist_p2 = i_case['вторичный показатель'].split(';')
            list_p2 = []
            # Добавляем параметр 1 он всегда один
            if 'check_' + p1.split('-')[0] in names:
                list_p2.append(p1)
            else:
                logger.error('Нарушение {} отсутствует в списке предусмотренных'.format(p1))
            if (len(llist_p2) > 0) and (len(llist_p2[0]) > 0):
                for ll in list(llist_p2):
                    if ll.split('-')[0] in names:
                        list_p2.append(ll)
                    else:
                        if not ll.split('-')[0].isspace():
                            logger.error(
                                'Вторичное нарушение {} отсутствует в списке предусмотренных'.format(ll.split('-')[0])
                            )
            str1 = ';'.join(str(e) for e in list_p2)
            if i_case['Причина'] in cases:
                s = cases[i_case['Причина']][1]
                s = s + ';' + str1
                cases[i_case['Причина']][1] = s
                cases[i_case['Причина']][0] += prop

            else:
                cases[i_case['Причина']] = [prop, str1]
        for c in cases:
            resdf = pd.concat(
                [
                    resdf,
                    pd.DataFrame.from_dict(
                        {'Причина': c, 'Вероятность': cases[c][0], 'Параметр': cases[c][1]}, orient='index'
                    ).T,
                ]
            )
            # resdf = resdf.append({'Причина': c, 'Вероятность': cases[c][0], 'Параметр': cases[c][1]}, ignore_index=True)
            # resdf['Вероятность'] = resdf['Вероятность'].round(decimals=2)

        return resdf

    def get_string_output(self):
        if len(self.alg_int.excepted_fields) > 0:
            ending = (
                f' Внимание! В данных отсутствуют показатели {"; ".join(self.alg_int.excepted_fields)}.'
                f' Интерпретация может быть неточной!'
            )
        else:
            ending = ''
        string_output = {}
        if self.aggr_res_dict['probability'] == '-':
            string_output['result'] = 'Превышения допустимых пределов не выявлено.'
        else:
            for n, row in pd.DataFrame(self.aggr_res_dict).iterrows():
                prefix = 'Выявлены отклонения: "' + row['deviation'] + '". '
                if row['probability'] > 0.5:
                    postfix = 'Причиной является ' + row['reason'] + '.'
                else:
                    postfix = (
                        'Есть риск "' + row['reason'] + '". Рекомендуем произвести дополнительный отбор и анализ пробы.'
                    )
                string_output['result'] = (prefix + postfix).replace(';', '; ').replace('-', ' - ')
        string_output['result'] = string_output['result'] + ending
        return string_output

    def make_output_dict(self):
        output_dict = {
            'measure': self.output_for_xls['Пров.показатель'],
            'deviation': self.output_for_xls['отклонение'],
            'reason': self.output_for_xls['Причина'],
            'total_probability': self.output_for_xls['Итоговая вероятность'],
            'confirmation': self.output_for_xls['Втор.показатель'],
        }

        return output_dict


def transform_to_need_format(x, num):
    """
    Функция по преобразованию в удобный формат.
    """
    buf = {
        'Проверяемый параметр': [x['Проверяемый параметр'].iloc[0]],
        'нарушение': [x['нарушение'].iloc[0]],
        'Причина': [x['Причина'].iloc[0]],
        'Вероятность': [
            x['Вероятность1'].iloc[0] + (x['Вероятность2(+)'] * x[num] + x['Вероятность2(-)'] * (x[num] - 1)).sum()
        ],
        'вторичный показатель': [
            ';'.join(
                [
                    value + '-' + ver
                    for value, ver in zip(x[x[num] == 1]['вторичный показатель'], x[x[num] == 1]['нарушение.1'])
                ]
            )
        ],
    }

    return pd.DataFrame.from_dict(buf)
