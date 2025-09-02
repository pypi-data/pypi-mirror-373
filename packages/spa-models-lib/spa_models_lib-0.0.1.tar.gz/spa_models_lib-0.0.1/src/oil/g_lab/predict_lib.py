# -*- coding: utf-8 -*-
import json
import logging as logger
import re

import numpy as np
import pandas as pd
from lib.calculator_builder import CalculatorPartBuilder, Director
from lib.flexible_limit_text_parser import FlexibleLimitPreprocessing
from lib.limit_text_parser import LimitProcessingFields
from lib.settings import *

# # # # История изменений: # # # #
# 13.11.2020 - Файл создан.
# 12.01.2021 - Обработка файла лимитов приведена в ОО формат
# 13.01.2021 - Расчет результатов прогноза оформлен в ОО формат
# 28.01.2021 - Исправлен формат с int32 на int для выходного json
# 12.02.2021 - Доработка по гибкому набору параметров
# 25.02.2021 - Адаптация к новому формату входных файлов
# # # # # # # # # # # # # # # # # #

# Класс входных лимитов
class InputLimit(object):
    def __init__(self, limit_path, _format_):
        self.path = limit_path
        self.format = _format_
        assert self.format in ['json', 'dictionary'], 'Input limit format is wrong!'
        if self.format == 'json':
            self.data = self.read_json()
        if self.format == 'dictionary':
            self.data = self.path

    def read_json(self):
        with open(self.path, 'r') as handle:
            limits = json.loads(handle.read())
        return limits


# Класс-адаптер для входных лимитов, делающий из входного формата нужный словарь
class AdapterInput2LimitDict(InputLimit):
    def __init__(self, limit_path, _format_, adapt_dict):
        super().__init__(limit_path, _format_)
        self.adapt_dict = adapt_dict
        if self.format == 'json':
            self.limits = self.json_transform()
        if self.format == 'dictionary':
            self.limits = self.dict_transform()

    def json_transform(self):
        buffer = {}
        for el in parameter_list:
            if el == 'TBN_TAN':
                buffer[el] = 0.0
            else:
                if el in self.data.keys():
                    if el in ['Viscosity100']:
                        buffer[el] = (self.data[el][0], self.data[el][1])
                    elif el in ['Pb', 'Nitration']:
                        buffer[el] = self.data[el][1]

        return {self.adapt_dict[k]: buffer[k] for k in buffer.keys()}

    def dict_transform(self):
        buffer = {}
        if all(type(value) == dict for value in self.data.values()):  # если используются гибкие лимиты
            for el in parameter_list:
                if el == 'TBN_TAN':
                    buffer[el] = {'lambda': 0.0, 'delta': 0.0}
                else:
                    if el in self.data.keys():
                        pars = FlexibleLimitPreprocessing(self.data[el])
                        buffer[el] = {'lambda': pars.trend, 'delta': pars.delta}
            return {self.adapt_dict[k]: buffer[k] for k in buffer.keys()}
        else:
            for el in self.data.keys():
                if el == 'TBN_TAN':
                    buffer[el] = {'low': 0.0}
                else:
                    if el in self.data.keys():
                        pars = LimitProcessingFields(self.data[el])
                        buffer[el] = pars.result
            result = {}
            for k in buffer.keys():
                if k in self.adapt_dict:
                    result[self.adapt_dict[k]] = buffer[k]
            return result

    @staticmethod
    def string_to_minmax(string):
        for from_rpl, to_rpl in zip([',', '>=', '=>', '=<', '<=', ' '], ['.', '≥', '≥', '≤', '≤', '']):
            string = string.replace(from_rpl, to_rpl)
        if (re.match(r'([<>≤≥]\d+\.?\d*);([<>≤≥]\d+\.?\d*)', string) is not None) and (
            re.match(r'([<>≤≥]\d+\.?\d*);([<>≤≥]\d+\.?\d*)', string).group() == string
        ):
            return float(re.search(r'[<≤](\d+\.?\d*)', string).group(1)), float(
                re.search(r'[>≥](\d+\.?\d*)', string).group(1)
            )
        elif (re.match(r'([<>≤≥]\d+\.?\d*)', string) is not None) and re.match(
            r'([<>≤≥]\d+\.?\d*)', string
        ).group() == string:
            return float(re.search(r'[<>≤≥](\d+\.?\d*)', string).group(1))
        else:
            logger.warning('Error in limits format')


# Класс Результатов расчетов
class PredictionResult(object):
    def __init__(self, input_json, lim_path):
        self.input_json = input_json
        if 'Horizont' in self.input_json:
            self.horizont = self.input_json['Horizont'][0]
        else:
            self.horizont = 2500

        # Загружаем предельные значения
        self.lim_path = lim_path
        self.limits = AdapterInput2LimitDict(
            limit_path=self.lim_path, _format_='dictionary', adapt_dict=to_rename_limits
        ).limits

        logger.info('Limits loaded successfully')
        logger.info('Limits: {}'.format(self.limits))

        # Преобразуем входные данные
        self.input_df = self.make_input_df()

        self.target, self.prediction, self.danger_time, self.target_time = self.calculate_prediction()
        self.plan_time = int(self.input_json['Time_table'][-1] * 24)
        logger.info('Predictions calculated successfully')
        logger.info('Danger times: {}'.format(self.danger_time))
        self.danger_param_in_input_data = []
        self.danger_param_in_predict = []
        self.danger_time_predict = []
        # Агрегируем результаты
        if bool(self.danger_time):
            self.result = self.calc_final_value()
            logger.info('Predictions aggregated successfully')
            logger.info('Result: {}'.format(self.result))
            # Стоим график прогноза и сохраняем его
            # self.fig, self.binary_fig = self.make_figure_and_save()
        else:
            logger.info('Result dictionary is empty')
            self.result = {
                'parameter': None,
                'value': None,
                'comment': 'Опасные значения не будут достигнуты в прогнозируемый период.',
                'result': 'Опасные значения не будут достигнуты в прогнозируемый период.',
            }
            # self.make_figure_and_save_empty()

        self.res = self.make_new_output()

    # TODO: заменить параметры в списках на названия на русском для сообщений
    def make_new_output(self):
        rename_lim = list({to_rename_limits[k] for k in set(self.lim_path.keys()) if k in set(to_rename_limits.keys())})
        param_in_limits = list(set(self.lim_path.keys()) - set(to_rename_limits.keys()))
        param_in_limits.extend(rename_lim)
        self.excepted_limits = rename_elements(
            list(
                set(self.input_df.columns)
                - set(param_in_limits)
                - set(['Horizont', 'operating_time', 'Change_time'])
                - set(string_fields)
            )
        )

        logger.info('Обязательные параметры в данных {}'.format(self.important_parameters))
        logger.info('Отсутвствующие обязательные параметры в данных {}'.format(self.excepted_import_fields))
        logger.info('Oтсутствуют в лимитах {}'.format(self.excepted_limits))
        logger.info('Отсутствуют обязательные параметры в лимитах {}'.format(self.excepted_limits_import))
        logger.info(
            'Отсутствуют необязательные параметры в лимитах {}'.format(
                set(self.excepted_limits) - set(self.excepted_limits_import)
            )
        )
        messages = self.get_string_output()
        res = self.result.copy()
        res['title'] = 'Прогноз интервала замены СМ'
        res['message'] = {}
        res['message']['owner'] = []
        res['message']['user'] = []
        if messages != {}:
            for msg in messages:
                if 'owner' in msg.keys():
                    if res['message']['owner'] != []:
                        res['message']['owner'].extend(msg['owner'])
                    else:
                        res['message']['owner'] = msg['owner']
                else:
                    if res['message']['user'] != []:
                        res['message']['user'].extend(msg['user'])
                    else:
                        res['message']['user'] = msg['user']
            msg_user = []
            for text in res['message']['user']:
                msg_user.append(text['text'])
            res['body'] = res['result'] + '<br>' + '<br> '.join(msg_user)
        else:
            res['body'] = res['result']
        return res

    def get_string_output(self):
        all_msg = []
        if len(self.excepted_import_fields) > 0:
            msg = [{'owner': [{'level': 'red', 'text': f''}]}, {'user': [{'level': 'red', 'text': f''}]}]
            all_msg.extend(msg)
        if len(self.excepted_limits) > 0:
            if len(self.excepted_limits_import) > 0:
                msg = [
                    {
                        'owner': [
                            {
                                'level': 'red',
                                'text': f'Ошибка в предельных значениях для показателей: {", ".join(sorted(self.excepted_limits))}. Из них обязательные: {", ".join(sorted(self.excepted_limits_import))}.',
                            }
                        ]
                    },
                    {'user': [{'level': 'red', 'text': ''}]},
                ]
                all_msg.extend(msg)
            elif len(set(self.excepted_limits) - set(self.excepted_limits_import)) > 0:
                msg = [
                    {
                        'owner': [
                            {
                                'level': 'red',
                                'text': f'Ошибка в предельных значениях для необязательных показателей: {", ".join(sorted(self.excepted_limits))}',
                            }
                        ]
                    },
                    {'user': [{'level': 'yellow', 'text': ''}]},
                ]
                all_msg.extend(msg)

        if self.danger_param_in_input_data:
            msg = [
                {
                    'owner': [
                        {
                            'level': 'red',
                            'text': f'Значения показателей ФХС в пробе: {self.danger_param_in_input_data} превышают предельные значения лимитов.',
                        }
                    ]
                },
                {
                    'user': [
                        {
                            'level': 'red',
                            'text': f'Значения показателей ФХС в пробе: {self.danger_param_in_input_data} превышают предельные значения лимитов.',
                        }
                    ]
                },
            ]
            all_msg.extend(msg)

        elif self.danger_param_in_predict:
            if self.danger_time_predict > self.plan_time:
                msg = [
                    {
                        'owner': [
                            {
                                'level': 'red',
                                'text': f'Опасные значения показателей ФХС: {self.danger_param_in_predict} достигаются при наработке около {self.danger_time_predict} мч. Момент наступает позднее следующего планового отбора пробы ({self.plan_time}). Рекомендуем обратить внимание на динамику изменения данного показателя. По результатам исследования следующей плановой пробы прогноз будет скорректирован.',
                            }
                        ]
                    },
                    {
                        'user': [
                            {
                                'level': 'red',
                                'text': f'Опасные значения показателей ФХС: {self.danger_param_in_predict} достигаются при наработке около {self.danger_time_predict} мч. Момент наступает позднее следующего планового отбора пробы ({self.plan_time}). Рекомендуем обратить внимание на динамику изменения данного показателя. По результатам исследования следующей плановой пробы прогноз будет скорректирован.',
                            }
                        ]
                    },
                ]
                all_msg.extend(msg)
            else:
                msg = [
                    {
                        'owner': [
                            {
                                'level': 'red',
                                'text': f'Опасные значения показателей ФХС: {self.danger_param_in_predict} достигаются при наработке около {self.danger_time_predict} мч. Момент наступает раньше следующего планового отбора пробы ({self.plan_time}). Рекомендуем провести внеплановый отбор и анализ пробы через {self.danger_time_predict} мч, отбор пробы внесен в график отбора.',
                            }
                        ]
                    },
                    {
                        'user': [
                            {
                                'level': 'red',
                                'text': f'Опасные значения показателей ФХС: {self.danger_param_in_predict} достигаются при наработке около {self.danger_time_predict} мч. Момент наступает раньше следующего планового отбора пробы ({self.plan_time}). Рекомендуем провести внеплановый отбор и анализ пробы через {self.danger_time_predict} мч, отбор пробы внесен в график отбора.',
                            }
                        ]
                    },
                ]
                all_msg.extend(msg)
        else:
            msg = [
                {
                    'owner': [
                        {'level': 'yellow', 'text': f'Опасные значения не будут достигнуты в прогнозируемый период.'}
                    ]
                },
                {
                    'user': [
                        {'level': 'yellow', 'text': f'Опасные значения не будут достигнуты в прогнозируемый период.'}
                    ]
                },
            ]
            all_msg.extend(msg)

        logger.info('Сообщения {}'.format(all_msg))
        return all_msg

    # Вычисление итогового значения
    def calc_final_value(self):
        result = {}
        values = np.array([i for i in self.danger_time.values()])
        keys = rename_elements(list(self.danger_time.keys()))
        # remove_index=[list(values).index(i) for i in list(values) if i==0]
        remove_index = []
        for i, p in enumerate(list(values)):
            if p == 0:
                remove_index.append(i)
        chk_list = list(values)
        for remove in reversed(remove_index):
            chk_list.pop(remove)
        if np.min(values) == -1:
            k = [keys[i[0]] for i in enumerate(values) if i[1] == np.min(values)]
            k.sort()
            k = '; '.join(k)
            comment = 'Опасное значение параметра(ов) {} достигнуто уже во входных данных.'.format(k)
            self.danger_param_in_input_data = k
            result['parameter'] = k
            result['value'] = int(np.min(values))
            result['comment'] = comment
            result['result'] = comment
        elif len(chk_list) > 0:
            for remove in reversed(remove_index):
                keys.pop(remove)
            dt = [i for i in values if i == np.min(chk_list)]
            if len(dt) > 0:
                k = [keys[i[0]] for i in enumerate(chk_list) if i[1] == np.min(chk_list)]
                k.sort()
                k = '; '.join(k)
                self.danger_param_in_predict = k
                self.danger_time_predict = int(np.min(chk_list) - self.input_json['Operating_time'][-1])
                if self.danger_time_predict > self.plan_time:
                    comment = (
                        f'Опасные значения показателей ФХС: {self.danger_param_in_predict} достигаются при'
                        f' наработке около {self.danger_time_predict} мч. Момент наступает позднее следующего'
                        f' планового отбора пробы ({self.plan_time}) мч. Рекомендуем обратить внимание на динамику'
                        f' изменения данного показателя. По результатам исследования следующей плановой пробы'
                        f' прогноз будет скорректирован.'
                    )
                else:
                    comment = (
                        f'Опасные значения показателей ФХС: {self.danger_param_in_predict} достигаются'
                        f' при наработке около {self.danger_time_predict} мч. Момент наступает раньше'
                        f' следующего планового отбора пробы ({self.plan_time}) мч. Рекомендуем провести '
                        f'внеплановый отбор и анализ пробы через {self.danger_time_predict} мч,'
                        f' отбор пробы внесен в график отбора.'
                    )
                result['parameter'] = self.danger_param_in_predict
                result['value'] = int(self.danger_time_predict)
                result['comment'] = comment
                result['result'] = comment

        else:
            comment = (
                f'В течении {self.horizont} мч предельных значений не прогнозируется.'
                f'Рекомендуем соблюдать плановый график отбора проб.'
            )
            k = keys[np.argmin(values)]
            result['parameter'] = k
            result['value'] = int(np.min(values))
            result['comment'] = comment
            result['result'] = comment
        return result

    # Функция вычисления прогнозов
    def calculate_prediction(self):
        director = Director(list(self.input_df.columns))
        director.builder = CalculatorPartBuilder(
            input_json=self.input_json, value_dataframe=self.input_df, limits_dict=self.limits
        )
        director.build_calculator()
        self.important_parameters = rename_elements(director.important_parameters)
        self.excepted_import_fields = rename_elements(director.excepted_import_fields)
        self.excepted_limits_import = rename_elements(director.excepted_limits_import)

        res = director._builder.total_prediction.return_res()
        target = res['target']
        prediction = res['prediction']
        danger_time = res['danger_time']
        target_time = res['target_time']

        return target, prediction, danger_time, target_time

    def make_input_df(self):
        input_df = pd.DataFrame(self.input_json).reset_index(drop=True)
        input_df.rename(columns=to_rename_input1, inplace=True)
        return input_df


# Функция построения графика прогноза
# def pred_plot(input_df, target, prediction, parameters, limits, result):
#     logger.info('Строим график из параметров: {}'.format(parameters))
#     if 'TBN_TAN' in parameters:
#         input_df['TBN_TAN'] = input_df.loc[:, 'TBN'] - input_df.loc[:, 'TAN']
#     fig, ax = plt.subplots(1, len(parameters))
#     fig.set_size_inches(20, 5)
#     for i, parameter in enumerate(parameters):
#         # if result['value'] == 0:
#         #     axis = ax[i] if len(parameters) > 1 else ax
#         #     sns.scatterplot(x=input_df['operating_time'], y=input_df[parameter], color='green',
#         #                     s=100, ax=axis)
#         # else:
#         axis = ax[i] if len(parameters) > 1 else ax
#         sns.scatterplot(x=input_df['operating_time'], y=input_df[parameter], color='green',
#                         s=100, ax=axis)
#         sns.scatterplot(x=target[parameter], y=prediction[parameter], color='red', marker='+', ax=axis)
#         if isinstance(limits[parameter], float) or isinstance(limits[parameter], int):
#             axis.scatter(np.arange(0, max(input_df['operating_time'].to_list() + list(target[parameter])), 10),
#                          np.repeat(limits[parameter],
#                                    len(np.arange(0,
#                                                  max(input_df['operating_time'].to_list() + list(target[parameter])),
#                                                  10))),
#                          marker='_', s=300, color='green')
#         elif isinstance(limits[parameter], tuple):
#             axis.scatter(np.arange(0, max(input_df['operating_time'].to_list() + list(target[parameter])), 10),
#                          np.repeat(limits[parameter][0],
#                                    len(np.arange(0,
#                                                  max(input_df['operating_time'].to_list() + list(target[parameter])),
#                                                  10))),
#                          marker='_', s=300, color='green')
#             axis.scatter(np.arange(0, max(input_df['operating_time'].to_list() + list(target[parameter])), 10),
#                          np.repeat(limits[parameter][1],
#                                    len(np.arange(0,
#                                                  max(input_df['operating_time'].to_list() + list(target[parameter])),
#                                                  10))),
#                          marker='_', s=300, color='green')
#         elif isinstance(limits[parameter], dict):
#             if 'high' in limits[parameter] and 'low' in limits[parameter]:
#                 x = np.arange(0, max(input_df['operating_time'].to_list() + list(target[parameter])), 10)
#
#                 lim_high = np.repeat(limits[parameter]['high'],
#                                    len(np.arange(0,max(input_df['operating_time'].to_list() + list(target[parameter])), 10)))
#
#                 lim_low = np.repeat(limits[parameter]['low'],
#                                 len(np.arange(0, max(input_df['operating_time'].to_list() + list(target[parameter])),
#                                               10)))
#                 axis.scatter(x, lim_high, marker='_', s=300, color='green')
#                 axis.scatter(x, lim_low, marker='_', s=300, color='green')
#             elif 'high' in limits[parameter] or 'low' in limits[parameter]:
#                 x = np.arange(0, max(input_df['operating_time'].to_list() + list(target[parameter])), 10)
#                 if 'high' in limits[parameter]:
#                     lim = np.repeat(limits[parameter]['high'],
#                                    len(np.arange(0,max(input_df['operating_time'].to_list() + list(target[parameter])), 10)))
#                 else:
#                     lim = np.repeat(limits[parameter]['low'],
#                                 len(np.arange(0, max(input_df['operating_time'].to_list() + list(target[parameter])),
#                                               10)))
#                 axis.scatter(x, lim, marker='_', s=300, color='green')
#
#             else:
#                 x = np.arange(0, max(input_df['operating_time'].to_list() + list(target[parameter])), 10)
#                 lim_low = limits[parameter]['lambda'](x) - limits[parameter]['delta']
#                 lim_high = limits[parameter]['lambda'](x) + limits[parameter]['delta']
#                 axis.scatter(x, lim_low, marker='_', s=300, color='green')
#                 axis.scatter(x, lim_high, marker='_', s=300, color='green')
#
#         axis.set_xlabel('Наработка масла, мч', size=8)
#         axis.set_ylabel(names[parameter], size=8)
#         if result['value'] == -1:
#             fig.suptitle('Критические значения параметров {} уже достигнуты во входных данных'.format(
#                 '; '.join([i for i in result['parameter'].split('; ')])),
#                 fontsize=20)
#         elif result['value'] == 0:
#             fig.suptitle('{}.'.format(
#                 result['comment']),
#                 fontsize=20)
#         elif len(result['parameter'].split('; ')) > 1:
#             fig.suptitle('Ближайшее крит. значение достигают {} при наработке около {} мч.'.format(
#                 '; '.join([i for i in result['parameter'].split('; ')]),
#                 result['value']),
#                 fontsize=20)
#         else:
#             fig.suptitle('Ближайшее крит. значение достигает {} при наработке около {} мч.'.format(
#                 result['parameter'],
#                 result['value']),
#                 fontsize=20)
#     img_dir = os.path.join(PATH, 'img')
#     if not os.path.exists(img_dir):
#         os.mkdir(img_dir)
#     img_path = os.path.join(img_dir, 'output_img.png')
#     fig.savefig(img_path, format='png')
#     return fig, img_path


def rename_elements(list_name):
    new_names = []
    for elem in list_name:
        if elem in to_rename_output.keys():
            new_names.append(to_rename_output[elem])
        else:
            new_names.append(elem)
    return new_names
