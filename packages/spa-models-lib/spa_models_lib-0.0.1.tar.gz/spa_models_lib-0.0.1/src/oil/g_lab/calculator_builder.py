# -*- coding: utf-8 -*-

# # # # История изменений: # # # #
# 12.02.2021 - Файл создан.
#
# # # # # # # # # # # # # # # # # #

import logging as logger
from abc import ABC

import numpy as np

from .model_module import ModelManager
from .settings import names, parameter_list


class CalculatorBuilder(ABC):
    """
    Интерфейс калькулятора прогноза. Создающие методы
    """

    def total_prediction(self, parameter):
        pass

    def Parameters_prediction(self, parameter):
        pass


class CalculatorPartBuilder(CalculatorBuilder):
    """
    Класс Конкретного Строителя.
    """

    def __init__(self, input_json, value_dataframe, limits_dict):
        self.reset()
        # Датафрейм с данными получаемыми для произведения операция расчета лимитов
        self.value_dataframe = value_dataframe
        self.limits_dict = limits_dict
        self.input_json = input_json
        self.target_time = dict()

        if 'Horizont' in self.input_json:
            self.horizont = int(self.input_json['Horizont'][0])
        else:
            self.horizont = 2500
        if 'operating_time' in self.value_dataframe.columns:
            oper_time = self.value_dataframe.operating_time.to_numpy()
            self.target_time['target_time'] = np.array(
                range(int(oper_time[-1] // 100 + 1) * 100, int(self.horizont), 100)
            )
            self.target_time['step'] = 100
            self._total_prediction.setTargetTime(self.target_time)
        else:
            logger.warning('Нет данных по наработке масла')

    def reset(self):
        self._total_prediction = CurrentPrediction()

    @property
    def total_prediction(self):
        total_prediction = self._total_prediction
        self.reset()
        return total_prediction

    def find_danger_value(self, parameter, series, target, prediction):
        limit = self.limits_dict[parameter]
        init_param = series
        limit_in_init = 0
        if parameter in list(set(parameter_list) | set(names) - set(['TBN_TAN'])):   # проверяем все, кроме TBN_TAN
            if 'high' in limit and 'low' in limit:
                if any([True if (i > limit['high']) or (i < limit['low']) else False for i in init_param]):
                    limit_in_init += 1
            elif 'high' in limit:
                if any([True if i > limit['high'] else False for i in init_param]):
                    limit_in_init += 1
            else:
                if any([True if i < limit['low'] else False for i in init_param]):
                    limit_in_init += 1

        if limit_in_init > 0:
            danger_time_cur = -1
            logger.info('Опасное значение параметра {} уже достигнуто во входных данных'.format(parameter))
        else:
            danger_time_cur = 0
            res_ind = 0
            for i, p in enumerate(prediction):
                if parameter in ['TBN_TAN']:   # проверяем разницу между щелочным и кислотным числом
                    if 'high' in limit:
                        if p >= limit['high']:
                            error_i = i  # - 1 if i >= 1 else 0
                            danger_time_cur = target[error_i]
                            logger.info(
                                'Опасное значение параметра {} будет достигнуто при наработке около {} мч'.format(
                                    parameter, danger_time_cur
                                )
                            )
                            res_ind += 1
                            break
                    else:
                        if p <= limit['low']:
                            error_i = i  # - 1 if i >= 1 else 0
                            danger_time_cur = target[error_i]
                            logger.info(
                                'Опасное значение параметра {} будет достигнуто при наработке около {} мч'.format(
                                    parameter, danger_time_cur
                                )
                            )
                            res_ind += 1
                            break
                elif parameter in list(
                    set(parameter_list) | set(names) - set(['TBN_TAN', 'TAN', 'TBN'])
                ):   ## проверяем все, кроме TBN и TAN
                    if 'high' in limit and 'low' in limit:
                        if (p > limit['high']) or (p < limit['low']):
                            error_i = i  # - 1 if i >= 1 else 0
                            danger_time_cur = target[error_i]
                            logger.info(
                                'Опасное значение параметра {} будет достигнуто при наработке около {} мч'.format(
                                    parameter, danger_time_cur
                                )
                            )
                            res_ind += 1
                            break
                    elif 'high' in limit:
                        if p > limit['high']:
                            error_i = i  # - 1 if i >= 1 else 0
                            danger_time_cur = target[error_i]
                            logger.info(
                                'Опасное значение параметра {} будет достигнуто при наработке около {} мч'.format(
                                    parameter, danger_time_cur
                                )
                            )
                            res_ind += 1
                            break
                    else:
                        if p < limit['low']:
                            error_i = i  # - 1 if i >= 1 else 0
                            danger_time_cur = target[error_i]
                            logger.info(
                                'Опасное значение параметра {} будет достигнуто при наработке около {} мч'.format(
                                    parameter, danger_time_cur
                                )
                            )
                            res_ind += 1
                            break

            if res_ind == 0:
                logger.info(
                    'Опасное значение параметра {} не достигается в пределах {} мч'.format(parameter, target[-1])
                )
        return danger_time_cur

    def filtering_first_probe(self, parameter):
        limit = self.limits_dict[parameter]
        if parameter == 'TBN_TAN':
            init_param = (self.value_dataframe.loc[:, 'TBN'] - self.value_dataframe.loc[:, 'TAN']).to_numpy()
        else:
            init_param = self.value_dataframe[parameter].to_numpy()
        oper_time = self.value_dataframe.operating_time.to_numpy()
        limit_in_probe = 0
        if parameter in list(set(parameter_list) | set(names) - set(['TBN_TAN'])):
            if 'high' in limit and 'low' in limit:
                if (init_param[0] > limit['high']) or (init_param[0] < limit['low']):
                    limit_in_probe += 1
            elif 'high' in limit:
                if init_param[0] > limit['high']:
                    limit_in_probe += 1
            else:
                if init_param[0] < limit['low']:
                    limit_in_probe += 1

        if limit_in_probe > 0:
            logger.warning(
                'Первая проба параметра {} не соответсвет заданным лимитам. Данное значение не используется для построения прогноза'.format(
                    parameter
                )
            )
            return init_param[1:], oper_time[1:]
        else:
            return init_param, oper_time

    def Parameters_prediction(self, parameter):
        try:
            res_first_probe = self.filtering_first_probe(parameter=parameter)
            parameter_series = res_first_probe[0]
            oper_time = res_first_probe[1]

            target = np.array(
                range(int(oper_time[-1] // 100 + 1) * 100, self.horizont, 100)
            )  # список значения времени для прогноза (начиная со следующей сотни и до 1000 мч)

            prediction = ModelManager(oper_time, parameter_series, target).forecasted_data

            self._total_prediction.setTarget(parameter=parameter, value=target)
            self._total_prediction.setPrediction(parameter=parameter, value=prediction)
            self._total_prediction.setDangerTime(
                parameter=parameter,
                value=self.find_danger_value(
                    parameter=parameter, series=parameter_series, target=target, prediction=prediction
                ),
            )
            logger.info(f'Для параметра {parameter} расчет прогноза успешно завершен')
        except Exception as e:
            logger.warning(f'Ошибка при расчете ограничений для параметра {parameter}. Текст ошибки:({e})')


class CurrentPrediction:
    def __init__(self):
        self.target = {}
        self.prediction = {}
        self.danger_time = {}
        self.target_time = {}

    def setTargetTime(self, value):
        self.target_time = value

    def setTarget(self, parameter, value):
        self.target[parameter] = value

    def setPrediction(self, parameter, value):
        self.prediction[parameter] = value

    def setDangerTime(self, parameter, value):
        self.danger_time[parameter] = value

    def show_res(self):
        print('target:{}, prediction:{}, danger_time:{}'.format(self.target, self.prediction, self.danger_time))

    def return_res(self):
        return {
            'target': self.target,
            'prediction': self.prediction,
            'danger_time': self.danger_time,
            'target_time': self.target_time,
        }


class Director:
    def __init__(self, column_titles: list):
        if not isinstance(column_titles, list):
            raise TypeError
        self._builder = None
        self.column_titles = column_titles
        self.predicted_fields = []
        self.excepted_fields = []
        self.important_parameters = []  # список обязательных парамтеров
        self.excepted_import_fields = []  # список отсутствующих обязательных параметров
        self.excepted_limits_import = []  # отсутствующие в лимитах среди обязательных

    @property
    def builder(self):
        return self._builder

    @builder.setter
    def builder(self, builder: CalculatorBuilder):
        self._builder = builder

    def build_calculator(self):
        logger.info('Инициализация методов и настроек для построения прогнозов')
        fields_prop_methods = {
            'Viscosity40': {
                'method': self.builder.Parameters_prediction,
                'dependency': ['operating_time'],
                'derivative': False,
            },
            'nitration': {
                'method': self.builder.Parameters_prediction,
                'dependency': ['operating_time'],
                'derivative': False,
            },
            'Pb': {'method': self.builder.Parameters_prediction, 'dependency': ['operating_time'], 'derivative': False},
            'TAN': {
                'method': self.builder.Parameters_prediction,
                'dependency': ['operating_time'],
                'derivative': False,
            },
            'sulfation': {
                'method': self.builder.Parameters_prediction,
                'dependency': ['operating_time'],
                'derivative': False,
            },
            'oxidation': {
                'method': self.builder.Parameters_prediction,
                'dependency': ['operating_time'],
                'derivative': False,
            },
        }
        logger.info(f'Входные данные содержат следующие параметры для обработки: {self.column_titles}')

        # Проверяем какие из необходимых параметров отсутствуют во входных данных или лимитах
        fields_for_prediction = []
        missing_fields_in_data = []
        missing_fields_in_limits = []
        self.important_parameters = list(fields_prop_methods.keys())
        for f in set(fields_prop_methods.keys()):
            if all([True if i in self.column_titles else False for i in fields_prop_methods[f]['dependency']]):
                if f in self._builder.limits_dict:
                    if fields_prop_methods[f]['derivative']:
                        fields_for_prediction.append(f)
                    elif f in self.column_titles:
                        fields_for_prediction.append(f)
                    else:
                        missing_fields_in_data.append(f)
                else:
                    missing_fields_in_limits.append(f)
            else:
                missing_fields_in_data.extend(
                    [i for i in fields_prop_methods[f]['dependency'] if i not in self.column_titles]
                )
        if len(missing_fields_in_data) > 0:
            logger.info(f'Входные данные не содержат следующих обязательных параметров: {missing_fields_in_data}.')
            self.excepted_import_fields.extend(missing_fields_in_data)
            self.excepted_fields.extend(missing_fields_in_data)
        if len(missing_fields_in_limits) > 0:
            logger.info(f'Лимиты не содержат следующих обязательных параметров: {missing_fields_in_limits}.')
            self.excepted_fields.extend(missing_fields_in_limits)
            self.excepted_limits_import.extend(missing_fields_in_limits)
        self.excepted_fields = list(set(self.excepted_fields))

        if len(fields_for_prediction) > 0:
            logger.info('Используются следующие параметры для построения прогноза: {}'.format(fields_for_prediction))
        else:
            logger.warning('Нет ни одного параметра, пригодного для построения прогноза')

        for column_title in fields_for_prediction:
            method_link = fields_prop_methods.get(column_title, None)
            if method_link is not None:
                method = method_link['method']
                method(parameter=column_title)
            else:
                logger.info(f'Параметр {column_title} из входных данных не используется для прогноза.')

        if len(self.excepted_fields) == 0:
            logger.info('Все необходимые параметры проанализированы, пропущенные - отсутствуют!')
