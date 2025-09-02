import logging as logger

import numpy as np
from scipy.optimize import curve_fit


class ModelManager:
    def __init__(self, x_data, y_data, target_timeseries):
        # self.loss = 0
        self.loss = float('inf')
        self.x_data = x_data
        self.y_data = y_data
        self.model = None
        self.forecasted_data = None
        self.target_timeseries = target_timeseries
        self.func = None  # коэффициенты функции тренда
        self.core_selector()

    @staticmethod
    def loss_method(x_data, y_data, model):
        return np.sqrt((y_data - model(x_data)) ** 2).mean()
        # return r2_score(y_data, model(x_data))

    def make_linear_forecast(self):
        # линейная модель
        func = lambda x, a, b: a * x + b
        # popt, pcov = curve_fit(func, self.x_data, self.y_data)

        popt = np.polyfit(self.x_data, self.y_data, 1)
        model = lambda x: popt[0] * x + popt[1]
        loss = self.loss_method(x_data=self.x_data, y_data=self.y_data, model=model)
        if self.forecasted_data is None:
            self.loss = loss
            self.forecasted_data = model(self.target_timeseries)
            self.model = model
            self.func = {'a': round(popt[0], 6), 'b': round(popt[1], 6)}
            self.type_model = 'linear'

        elif self.loss > loss:
            self.loss = loss
            self.forecasted_data = model(self.target_timeseries)
            self.model = model
            self.func = {'a': round(popt[0], 6), 'b': round(popt[1], 6)}
            self.type_model = 'linear'

    def make_poly_forecast(self):
        # Полиномиальная модель
        bound_list = []
        bound_list.append(((-np.inf, -np.inf, -np.inf), (np.inf, np.inf, np.inf)))
        for bounds in bound_list:
            try:

                func = lambda x, a, b, c: a * x**b + c
                # bounds = ((-np.inf, 1, -np.inf), (np.inf, np.inf, np.inf))
                popt, pcov = curve_fit(func, self.x_data, self.y_data, bounds=bounds, maxfev=10000)
                model = lambda x: popt[0] * x ** popt[1] + popt[2]

                loss = self.loss_method(x_data=self.x_data, y_data=self.y_data, model=model)
                if self.forecasted_data is None:
                    self.loss = loss
                    self.forecasted_data = model(self.target_timeseries)
                    self.model = model
                    self.func = {'a': round(popt[0], 6), 'b': round(popt[1], 6), 'c': round(popt[2], 6)}
                    self.type_model = 'poly'

                elif self.loss > loss:
                    self.loss = loss
                    self.forecasted_data = model(self.target_timeseries)
                    self.model = model
                    self.func = {'a': round(popt[0], 6), 'b': round(popt[1], 6), 'c': round(popt[2], 6)}
                    self.type_model = 'poly'

            except (RuntimeError, ValueError):
                logger.warning('Превышены ограничения на количество итераций подбора коэффициентов функции')

    #
    def make_exponential_forecast(self):
        # Полиномиальная экспоненциальная  модель
        # for alpha in np.arange(alpha_range[0], alpha_range[1], alpha_range[2]):
        func = lambda x, b, alpha: (alpha**x) + b
        bounds = ((-np.inf, -np.inf), (np.inf, np.inf))
        popt, pcov = curve_fit(func, self.x_data, self.y_data, bounds=bounds, maxfev=5000)
        model = lambda x: (popt[1] ** x) + popt[0]
        loss = self.loss_method(x_data=self.x_data, y_data=self.y_data, model=model)
        if self.forecasted_data is None:
            self.loss = loss
            self.forecasted_data = model(self.target_timeseries)
            self.model = model
            self.type_model = 'exp'
        elif self.loss > loss:
            self.loss = loss
            self.forecasted_data = model(self.target_timeseries)
            self.model = model
            self.type_model = 'exp'

    def core_selector(self):
        # Модуль выбора модели
        for method, core in {
            'linear': self.make_linear_forecast,
            'poly': self.make_poly_forecast,
            'exp': self.make_exponential_forecast,
        }.items():
            if len(self.y_data.tolist()) <= 2:
                if method == 'linear':
                    logger.info('Данных мало, прогноз может быть недостаточно качественным! Строится линейная модель!')
                    core()
            else:
                core()
