# -*- coding: utf-8 -*-

import logging as logger


class FlexibleLimitPreprocessing(object):
    def __init__(self, x):
        self.parsed_str = x
        logger.info('Parsing string: {}'.format(self.parsed_str))
        self.data_parser()

    def data_parser(self):
        if self.parsed_str['coef'] == 'None':
            self.trend = 'None'
            self.delta = 'None'
        else:
            self.delta = self.parsed_str['delta']
            if 'c' in self.parsed_str['coef']:
                self.trend = (
                    lambda x, a=self.parsed_str['coef']['a'], b=self.parsed_str['coef']['b'], c=self.parsed_str['coef'][
                        'c'
                    ]: a
                    * x**b
                    + c
                )
            else:
                self.trend = lambda x, a=self.parsed_str['coef']['a'], b=self.parsed_str['coef']['b']: a * x + b
