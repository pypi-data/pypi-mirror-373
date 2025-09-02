# -*- coding: utf-8 -*-
import logging as logger
import re

import numpy as np


class LimitProcessingFields(object):
    def __init__(self, x: str, dataset={}, input_dict={}):
        self.data = dataset
        self.indicators = list(input_dict.keys())
        self.input = input_dict
        self.parsed_str = x
        if 'TBN' in self.input and '%' in self.parsed_str:
            self.first_tbn = self.input['TBN'][0]
        else:
            self.first_tbn = None

        self.ops = {
            '<': (lambda x, y: x < y),
            '>': (lambda x, y: x > y),
            '≥': (lambda x, y: x >= y),
            'None': (lambda _: _),
            '≤': (lambda x, y: x <= y),
        }
        self.result = self.data_parser()
        self.get_result()
        logger.info('Parsing string: from {} to {}'.format(self.parsed_str, self.result))

    def get_result(self):
        return self.result

    def calc(self, val):

        if float(val) <= self.result.get('low', -np.inf):
            return 0
        elif float(val) >= self.result.get('high', np.inf):
            return 1
        else:
            return 2

    def data_parser(self):
        if self.parsed_str is not None:
            for from_rpl, to_rpl in zip([',', '>=', '=>', '=<', '<=', ' '], ['.', '≥', '≥', '≤', '≤', '']):
                self.parsed_str = self.parsed_str.replace(from_rpl, to_rpl)
            for indicator in self.indicators:
                if indicator in self.parsed_str:
                    if self.input[indicator][-1] != None:
                        value = self.input[indicator][-1]
                        return self.comparison_module(str(self.parsed_str[0] + str(value)))
                    elif self.input[indicator][-2] != None:
                        value = self.input[indicator][-2]
                        return self.comparison_module(str(self.parsed_str[0] + str(value)))
                    else:
                        self.none_field()
            if '%' in self.parsed_str and self.first_tbn is not None:   # обрботка лимита типа процентного соотношения
                value = float(re.sub('[><%]', '', self.parsed_str)) / 100
                return self.comparison_module(str(self.parsed_str[0] + str(self.first_tbn * value)))
            else:
                self.none_field()
            if ';' in self.parsed_str:
                return self.multiple_field(self.parsed_str)
            else:
                return self.comparison_module(self.parsed_str)
        else:
            return self.none_field()

    def indicator_field(self):
        found_indicators = re.findall('\w+', self.parsed_str)
        for indicator in found_indicators:
            indicator = re.sub('[><≥≤;]', '', indicator)
            indicator_value = self.data.get(indicator)
            self.parsed_str = re.sub(indicator, re.sub('[><≥≤;]', '', indicator_value), self.parsed_str)
        if ';' in self.parsed_str:
            return self.multiple_field(self.parsed_str)
        else:
            return self.comparison_module(self.parsed_str)

    def none_field(self):
        return self.ops['None'](True)

    def multiple_field(self, comparison):
        comparison = comparison.split(';')
        res_m_field = {}
        num_expression = ['≥', '≤']
        for num, comparison_element in enumerate(comparison):
            if not bool(re.findall('[><≥≤]', comparison_element)):
                comparison_element = num_expression[num] + comparison_element
            res_m_field.update(self.comparison_module(comparison_element))
        return res_m_field

    def comparison_module(self, comparison):
        found_operators = re.findall('[><≥≤]', comparison)
        for operator in found_operators:
            if operator in ['≥', '≤']:
                return self.soft_comparison_field(comparison)
            elif operator in ['>', '<']:
                return self.hard_comparison_field(comparison)

    def soft_comparison_field(self, comparison):
        if bool(re.search('≤', comparison)):
            if self.is_number(re.sub('≤', '', comparison)):
                return {'low': float(re.sub('≤', '', comparison))}
        elif bool(re.search('≥', comparison)):
            if self.is_number(re.sub('≥', '', comparison)):
                return {'high': float(re.sub('≥', '', comparison))}

    def hard_comparison_field(self, comparison):
        if bool(re.search('<', comparison)):
            if self.is_number(re.sub('<', '', comparison)):
                return {'low': float(re.sub('<', '', comparison))}
        elif bool(re.search('>', comparison)):
            if self.is_number(re.sub('>', '', comparison)):
                return {'high': float(re.sub('>', '', comparison))}

    @staticmethod
    def is_number(n):
        try:
            float(n)
        except ValueError:
            return False
        return True
