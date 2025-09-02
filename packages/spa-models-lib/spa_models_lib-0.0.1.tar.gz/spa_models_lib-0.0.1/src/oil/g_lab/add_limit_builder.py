# -*- coding: utf-8 -*-

import logging as logger
from abc import ABC

# # # # История изменений: # # # #
# 12.02.2021 - Файл создан.
#
# # # # # # # # # # # # # # # # # #


class AddLimitBuilder(ABC):
    """
    Интерфейс Строителя. Создающие методы проверок
    """

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

    # TODO: Добавить методы создания кусков лимитов, как на примере ниже

    def Viscosity40_operating(self, title):
        pass

    def TAN_operating(self, title):
        pass

    def Water_operating(self, title):
        pass

    def Zn_operating(self, title):
        pass

    def FlashPoint_operating(self, title):
        pass

    def Corrosiveness_operating(self, title):
        pass

    def Flash_point_operating(self, title):
        pass

    def Color_operating(self, title):
        pass

    def Al_operating(self, title):
        pass

    def Cr_operating(self, title):
        pass

    def Cu_operating(self, title):
        pass

    def Fe_operating(self, title):
        pass

    def Pb_operating(self, title):
        pass

    def K_operating(self, title):
        pass

    def Na_operating(self, title):
        pass

    def Si_operating(self, title):
        pass

    def Sn_operating(self, title):
        pass

    def Operating_time_operating(self, title):
        pass


class AddLimitPartBuilder(AddLimitBuilder):
    """
    Класс Конкретного Строителя.
    """

    def __init__(self, value_dataframe, limits_dataframe):
        self.operation_time_limit = 25000
        self.reset(value_dataframe)
        # Датафрейм с данными получаемыми для произведения операция расчета лимитов
        self.value_dataframe = value_dataframe
        self.limits_dataframe = limits_dataframe

    def reset(self, value_dataframe):
        self._product = CheckDataframe(value_dataframe)

    @property
    def product(self):
        product = self._product
        self.reset(self.limits_dataframe)
        return product

    def Viscosity40_operating(self, title='кинематическая вязкость при 40 °с'):
        try:
            l_func = self.limits_dataframe[self.limits_dataframe['Описание'] == title]['lambda'].iloc[0]
            self._product.setData(
                limit_title=title, limit_values=self.value_dataframe[title].apply(lambda x: l_func.calc(x))
            )
            logger.info(
                f'Для параметра {title} расчет ограничений успешно завершен {self.value_dataframe[title].apply(lambda x: l_func.calc(x))}'
            )
        except Exception as e:
            logger.error(f'Ошибка при расчете ограничений для параметра {title}. Текст ошибки:({e})')

    def Viscosity100_operating(self, title='кинематическая вязкость, при 100°c'):
        try:
            l_func = self.limits_dataframe[self.limits_dataframe['Описание'] == title]['lambda'].iloc[0]
            self._product.setData(
                limit_title=title, limit_values=self.value_dataframe[title].apply(lambda x: l_func.calc(x))
            )
            logger.info(
                f'Для параметра {title} расчет ограничений успешно завершен {self.value_dataframe[title].apply(lambda x: l_func.calc(x))}'
            )
        except Exception as e:
            logger.error(f'Ошибка при расчете ограничений для параметра {title}. Текст ошибки:({e})')

    def TAN_operating(self, title='кислотное число'):
        try:
            l_func = self.limits_dataframe[self.limits_dataframe['Описание'] == title]['lambda'].iloc[0]

            self._product.setData(
                limit_title=title, limit_values=self.value_dataframe[title].apply(lambda x: l_func.calc(x))
            )
            logger.info(
                f'Для параметра {title} расчет ограничений успешно завершен {self.value_dataframe[title].apply(lambda x: l_func.calc(x))}'
            )
        except Exception as e:
            logger.error(f'Ошибка при расчете ограничений для параметра {title}. Текст ошибки:({e})')

    def Water_operating(self, title='вода'):
        try:
            l_func = self.limits_dataframe[self.limits_dataframe['Описание'] == title]['lambda'].iloc[0]
            self._product.setData(
                limit_title=title, limit_values=self.value_dataframe[title].apply(lambda x: l_func.calc(x))
            )
            logger.info(f'Для параметра {title} расчет ограничений успешно завершен')
        except Exception as e:
            logger.error(f'Ошибка при расчете ограничений для параметра {title}. Текст ошибки:({e})')

    def Zn_operating(self, title='цинк'):
        try:
            l_func = self.limits_dataframe[self.limits_dataframe['Описание'] == title]['lambda'].iloc[0]
            self._product.setData(
                limit_title=title, limit_values=self.value_dataframe[title].apply(lambda x: l_func.calc(x))
            )
            logger.info(f'Для параметра {title} расчет ограничений успешно завершен')
        except Exception as e:
            logger.error(f'Ошибка при расчете ограничений для параметра {title}. Текст ошибки:({e})')

    def Al_operating(self, title='алюминий'):
        try:
            l_func = self.limits_dataframe[self.limits_dataframe['Описание'] == title]['lambda'].iloc[0]
            self._product.setData(
                limit_title=title, limit_values=self.value_dataframe[title].apply(lambda x: l_func.calc(x))
            )
            logger.info(f'Для параметра {title} расчет ограничений успешно завершен')
        except Exception as e:
            logger.error(f'Ошибка при расчете ограничений для параметра {title}. Текст ошибки:({e})')

    def Cr_operating(self, title='хром'):
        try:
            l_func = self.limits_dataframe[self.limits_dataframe['Описание'] == title]['lambda'].iloc[0]
            self._product.setData(
                limit_title=title, limit_values=self.value_dataframe[title].apply(lambda x: l_func.calc(x))
            )
            logger.info(f'Для параметра {title} расчет ограничений успешно завершен')
        except Exception as e:
            logger.error(f'Ошибка при расчете ограничений для параметра {title}. Текст ошибки:({e})')

    def Cu_operating(self, title='медь'):
        try:
            l_func = self.limits_dataframe[self.limits_dataframe['Описание'] == title]['lambda'].iloc[0]
            self._product.setData(
                limit_title=title, limit_values=self.value_dataframe[title].apply(lambda x: l_func.calc(x))
            )
            logger.info(f'Для параметра {title} расчет ограничений успешно завершен')
        except Exception as e:
            logger.error(f'Ошибка при расчете ограничений для параметра {title}. Текст ошибки:({e})')

    def Fe_operating(self, title='железо'):
        try:
            l_func = self.limits_dataframe[self.limits_dataframe['Описание'] == title]['lambda'].iloc[0]
            self._product.setData(
                limit_title=title, limit_values=self.value_dataframe[title].apply(lambda x: l_func.calc(x))
            )
            logger.info(f'Для параметра {title} расчет ограничений успешно завершен')
        except Exception as e:
            logger.error(f'Ошибка при расчете ограничений для параметра {title}. Текст ошибки:({e})')

    def Pb_operating(self, title='свинец'):
        try:
            l_func = self.limits_dataframe[self.limits_dataframe['Описание'] == title]['lambda'].iloc[0]
            self._product.setData(
                limit_title=title, limit_values=self.value_dataframe[title].apply(lambda x: l_func.calc(x))
            )
            logger.info(f'Для параметра {title} расчет ограничений успешно завершен')
        except Exception as e:
            logger.error(f'Ошибка при расчете ограничений для параметра {title}. Текст ошибки:({e})')

    def K_operating(self, title='кальций'):
        try:
            l_func = self.limits_dataframe[self.limits_dataframe['Описание'] == title]['lambda'].iloc[0]
            self._product.setData(
                limit_title=title, limit_values=self.value_dataframe[title].apply(lambda x: l_func.calc(x))
            )
            logger.info(f'Для параметра {title} расчет ограничений успешно завершен')
        except Exception as e:
            logger.error(f'Ошибка при расчете ограничений для параметра {title}. Текст ошибки:({e})')

    def Na_operating(self, title='натрий'):
        try:
            l_func = self.limits_dataframe[self.limits_dataframe['Описание'] == title]['lambda'].iloc[0]
            self._product.setData(
                limit_title=title, limit_values=self.value_dataframe[title].apply(lambda x: l_func.calc(x))
            )
            logger.info(f'Для параметра {title} расчет ограничений успешно завершен')
        except Exception as e:
            logger.error(f'Ошибка при расчете ограничений для параметра {title}. Текст ошибки:({e})')

    def Si_operating(self, title='кремний'):
        try:
            l_func = self.limits_dataframe[self.limits_dataframe['Описание'] == title]['lambda'].iloc[0]
            self._product.setData(
                limit_title=title, limit_values=self.value_dataframe[title].apply(lambda x: l_func.calc(x))
            )
            logger.info(f'Для параметра {title} расчет ограничений успешно завершен')
        except Exception as e:
            logger.error(f'Ошибка при расчете ограничений для параметра {title}. Текст ошибки:({e})')

    def Sn_operating(self, title='олово'):
        try:
            l_func = self.limits_dataframe[self.limits_dataframe['Описание'] == title]['lambda'].iloc[0]
            self._product.setData(
                limit_title=title, limit_values=self.value_dataframe[title].apply(lambda x: l_func.calc(x))
            )
            logger.info(f'Для параметра {title} расчет ограничений успешно завершен')
        except Exception as e:
            logger.error(f'Ошибка при расчете ограничений для параметра {title}. Текст ошибки:({e})')

    def Operating_time_operating(self, title='наработка масла'):
        try:
            l_func = self.limits_dataframe[self.limits_dataframe['Описание'] == title]['lambda'].iloc[0]
            self._product.setData(
                limit_title=title, limit_values=self.value_dataframe[title].apply(lambda x: l_func.calc(x))
            )
            logger.info(f'Для параметра {title} расчет ограничений успешно завершен')
        except Exception as e:
            logger.error(f'Ошибка при расчете ограничений для параметра {title}. Текст ошибки:({e})')


class CheckDataframe:
    def __init__(self, value_dataframe):
        self.value_dataframe = value_dataframe

    def setData(self, limit_title, limit_values):
        self.value_dataframe[f'check_{limit_title}'] = limit_values

    def show_df(self):
        print(f'Лимиты:\n {self.value_dataframe}')

    def return_df(self):
        return self.value_dataframe


class Director:
    def __init__(self, globClass, column_titles: list):
        if not isinstance(column_titles, list):
            raise TypeError
        self.globclass = globClass
        self._builder = None
        self.column_titles = column_titles
        self.checked_fields = []
        self.excepted_fields = []

    @property
    def builder(self):
        return self._builder

    @builder.setter
    def builder(self, builder: AddLimitBuilder):
        self._builder = builder

    def build_limits(self):

        logger.info('Инициализация методов и настроек для построения проверок на ограничения')
        pressure = []
        t_shaft = []
        # Формирование виртуальных функций имен для Давления и Температуру подшибника
        for i in self.globclass.tag_connection:
            if 'давление масла' in i.lower():
                pressure.append((i.split(' ')[2]).lower())
            if 'температура подшипника вала компрессора' in i.lower():
                l = len(self.globclass.tag_connection[i].split('|'))
                t_shaft = [str(i) for i in range(l)]

        # Задаем методы обрабоки с правилами обработки
        fields_prop_methods = {
            'кинематическая вязкость при 40 °с': {
                'method': self.builder.Viscosity40_operating,
                'limits': True,
                'extnema': [],
                'type': 'no',
            },
            'кинематическая вязкость, при 100°c': {
                'method': self.builder.Viscosity100_operating,
                'limits': True,
                'extnema': [],
                'type': 'no',
            },
            'вода': {'method': self.builder.Water_operating, 'limits': True, 'extnema': [], 'type': 'no'},
            'цинк': {'method': self.builder.Zn_operating, 'limits': True, 'extnema': [], 'type': 'no'},
            'алюминий': {'method': self.builder.Al_operating, 'limits': True, 'extnema': [], 'type': 'no'},
            'хром': {'method': self.builder.Cr_operating, 'limits': True, 'extnema': [], 'type': 'no'},
            'медь': {'method': self.builder.Cu_operating, 'limits': True, 'extnema': [], 'type': 'no'},
            'железо': {'method': self.builder.Fe_operating, 'limits': True, 'extnema': [], 'type': 'no'},
            'железо': {'method': self.builder.Fe_operating, 'limits': True, 'extnema': [], 'type': 'no'},
            'свинец': {'method': self.builder.Pb_operating, 'limits': True, 'extnema': [], 'type': 'no'},
            'кальций': {'method': self.builder.K_operating, 'limits': True, 'extnema': [], 'type': 'no'},
            'натрий': {'method': self.builder.Na_operating, 'limits': True, 'extnema': [], 'type': 'no'},
            'кремний': {'method': self.builder.Si_operating, 'limits': True, 'extnema': [], 'type': 'no'},
            'олово': {'method': self.builder.Sn_operating, 'limits': True, 'extnema': [], 'type': 'no'},
            'наработка масла': {
                'method': self.builder.Operating_time_operating,
                'limits': True,
                'extnema': [],
                'type': 'no',
            },
            'кислотное число': {'method': self.builder.TAN_operating, 'limits': True, 'extnema': [], 'type': 'no'},
        }

        logger.info(f'Входные данные содержат следующие параметры для обработки: {self.column_titles}')
        missing_fields = []
        for f in set(fields_prop_methods.keys()):
            if f not in [x.split('%')[0] for x in self.column_titles]:
                missing_fields.append(f)
        # missing_fields = [f for f in set(fields_prop_methods.keys()) if f not in self.column_titles]

        if len(missing_fields) > 0:
            logger.info(f'Нет функции обработки для параметров: {missing_fields}.')
            self.excepted_fields.extend(missing_fields)

        names_indata = list(set([x.split('%')[0] for x in self._builder.limits_dataframe['Описание']]))
        names_alg = [x.split('%')[0] for x in self.column_titles]
        for column_title_base in names_indata:
            method_link = fields_prop_methods.get(column_title_base, None)
            if method_link is not None:
                column_title = column_title_base

                dependency = method_link.get('dependency', [])
                method = method_link['method']
                if all([True if d in names_indata else False for d in dependency]):
                    logger.info(f'Для параметра {column_title} присутствуют все необходимые зависимости')
                    if method_link.get('limits', False):
                        if column_title_base in list(names_alg):
                            logger.info(f'Для параметра {column_title} найдены необходимые ограничения из списка')
                            logger.info(f'Вызов метода расчета проверки для параметра {column_title}')
                            if method_link['type'] == 'and':
                                method(title=column_title, list_ext=method_link['extnema'])
                            elif method_link['type'] == 'no':
                                method(title=column_title_base)
                            elif method_link['type'] == 'or':
                                method(title=column_title_base, list_ext=method_link['extnema'])
                            self.checked_fields.append(column_title)
                        else:
                            logger.info(
                                f'Для параметра {column_title} не найдены ограничения в списке лимитов. Параметр игнорируется'
                            )
                            self.excepted_fields.append(column_title)
                            continue
                    else:
                        logger.info(f'Параметр {column_title} не использует ограничения при расчете')
                        logger.info(f'Вызов метода расчета проверки для параметра {column_title}')
                        # method(title=column_title)
                        # self.checked_fields.append(column_title)
                else:
                    logger.info(
                        f'Для параметра {column_title} отсутствуют параметры, необходимые для расчета. Параметр игнорируется'
                    )
                    self.excepted_fields.append(column_title)
                    continue
            else:
                logger.info(f'Параметр {column_title_base} нет метода обработки!!!!!')

        if len(self.excepted_fields) == 0:
            logger.info('Все необходимые параметры проанализированы, пропущенные - отсутствуют!')
