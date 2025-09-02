# -*- coding: utf-8 -*-
import logging as logger
import re

import numpy as np
import pandas as pd

from .settings import PATH, parameter_list_not_predict, string_fields, to_rename_input

# # # # История изменений: # # # #
# 18.12.2020 - Файл создан.
# 25.12.2020 - Скорректирован расчет с учетом наличия строковых полей во входном json
# 25.01.2021 - Проверка переведена в объектный формат
#
#
# # # # # # # # # # # # # # # # # #

pd.options.mode.use_inf_as_na = True


class InputCheck(object):
    def __init__(self, input_dictionary, limits_dictionary):
        self.input_dictionary = {
            k: input_dictionary[k]
            for k in input_dictionary.keys()
            if k in list(to_rename_input.keys()) + ['operation_time']
        }

        self.limits_dictionary = limits_dictionary

        self.status = self.input_check_status() and self.limit_check_status()

    def input_check_status(self):
        str_d = {i: self.input_dictionary.get(i) for i in string_fields}
        non_str_d = {
            i: self.input_dictionary.get(i)
            for i in (set(self.input_dictionary) - set(string_fields) - set(parameter_list_not_predict))
        }

        if numeric_fields_check(non_str_d) and non_numeric_fields_check(str_d):
            return True
        else:
            return False

    def limit_check_status(self):

        self.limits_dictionary = {i: replace_symbols(self.limits_dictionary[i]) for i in self.limits_dictionary}
        logger.info(self.limits_dictionary)
        if all([is_right_limit_string(self.limits_dictionary[i]) for i in self.limits_dictionary]):
            logger.info('All limits are in right format!')
            return True
        else:
            logger.info(
                'There is bad input limits: {}'.format(
                    {
                        i: self.limits_dictionary[i]
                        for i in self.limits_dictionary
                        if not is_right_limit_string(self.limits_dictionary[i])
                    }
                )
            )
            return False


def is_right_limit_string(string):
    if (
        (re.match(r'([<>≤≥]?\d+\.?\d*);([<>≤≥]?\d+\.?\d*)', string) is not None)
        and (re.match(r'([<>≤≥]?\d+\.?\d*);([<>≤≥]?\d+\.?\d*)', string).group() == string)
    ) or (
        (re.match(r'([<>≤≥]\d+\.?\d*)', string) is not None)
        and re.match(r'([<>≤≥]\d+\.?\d*)', string).group() == string
    ):
        return True
    else:
        return False


def replace_symbols(string):
    limit_string = string
    for from_rpl, to_rpl in zip([',', '>=', '=>', '=<', '<=', ' '], ['.', '≥', '≥', '≤', '≤', '']):
        limit_string = limit_string.replace(from_rpl, to_rpl)
    return limit_string


def is_missing(d):
    res = []
    for k in enumerate(d.keys()):
        if pd.Series(d[k[1]]).isna().sum() > 0:
            res.append((k[1], d[k[1]]))
    return res


def not_numeric(d):
    res = []
    for k in enumerate(d.keys()):
        if pd.Series(d[k[1]]).dtype == np.array:
            res.append((k[1], d[k[1]]))
    return res


def is_negative(d):
    res = []
    for k in enumerate(d.keys()):
        if (pd.Series(d[k[1]]) < 0).sum() > 0:
            res.append((k[1], d[k[1]]))
    return res


def numeric_fields_check(d):
    # Проверка на наличие нечисловых значений
    numeric_check = not_numeric(d)
    if len(numeric_check) > 0:
        for i in numeric_check:
            logger.warning('There is parameter with non-numeric data in numeric fields: {}:\n{}'.format(i[0], i[1]))
        return False
    else:
        logger.info('There is no non-numeric values in numeric fields!')

        # Проверка на наличие пустых значений
        missing_check = is_missing(d)
        if len(missing_check) > 0:
            for i in missing_check:
                logger.warning('There is parameter with missing values in numeric fields: {}:\n{}'.format(i[0], i[1]))
            return False
        else:
            logger.info('There is no missing values in numeric fields!')
            # Проверка на наличие отрицательных значений
            negative_check = is_negative(d)
            if len(negative_check) > 0:
                for i in negative_check:
                    logger.warning(
                        'There is parameter with negative values in numeric fields: {}:\n{}'.format(i[0], i[1])
                    )
                return False
            else:
                logger.info('There is no negative values in numeric fields!')
                return True


def non_numeric_fields_check(d):
    # Проверка на наличие пустых значений
    missing_check = is_missing(d)
    if len(missing_check) > 0:
        for i in missing_check:
            logger.warning('There is parameter with missing values in string fields: {}:\n{}'.format(i[0], i[1]))
        return False
    else:
        logger.info('There is no missing values in string fields!')
        return True
