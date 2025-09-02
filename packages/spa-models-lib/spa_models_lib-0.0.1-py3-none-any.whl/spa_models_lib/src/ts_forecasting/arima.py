import itertools
from warnings import filterwarnings
import numpy as np
import pandas as pd
import statsmodels.api as sm
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from spa_models_lib.src.ts_forecasting.base import TSForecasting

filterwarnings('ignore')


class ArimaModel(TSForecasting):
    """
    Класс, реализующий модель прогнозирования ARIMA.
    """

    def __init__(self, *args, **kwargs):
        """
        Метод инициализации модели.
        """

        # self.data_dicretization = '10min'
        pass

    def fit(self, data: pd.Series, auto: bool = True):
        """
        Метод, обучающий модель.

        Алгоритм:
        1. создание модели SARAIMAX с параметром частоты равным 10 минут;
        2. обучение модели;

        Аргументы:
        data (pd.Series): исходные данные;
        auto (bool): флаг автооптимизации параметров.
        """

        self.data = data
        self.model = sm.tsa.statespace.SARIMAX(
            self.data, freq='10T'
        )
        self.results = self.model.fit(disp=False, method='powell', low_memory=True)

        return self

    def predict(self, data: pd.Series, start_date: int, end_date: int):
        """
        Метод для предсказания.

        Алгоритм:
        1. вызов метода predict с указанием начальной и конечной даты.

        Аргументы:
        data (pd.Series): исходные данные;
        start_date (int): начальная дата;
        end_date (int): конечная дата.

        Возврат:
        preds (pd.Series): предсказания.
        """

        self.preds = self.model.predict(start=start_date, end=end_date)
        return self.preds

    def forecast(self, steps: int = 10):
        """
        Метод прогнозирования.

        Алгоритм:
        1. вызов метода forecast с указанием количества шагов.

        Аргументы:
        steps (int): количество шагов прогнозирования.

        Возврат:
        forecasts (pd.Series): прогноз.
        """

        self.forecasts = self.results.forecast(steps=10)

        return self.forecasts

    def fit_predict(self, data: pd.Series):
        """
        Метод, объединяющий обучение и предсказание.

        Алгоритм:
        1. вызов методы _setup_data для предобработки данных;
        2. разделение данных на обучающую и тестовую выборки;
        3. обучение модели;
        4. предсказание на тестовом наборе с указанием начальных и конечных дат.

        Аргументы:
        data (pd.Series): исходные данные.
        """

        self.data = data
        processed_data = self.__setup_data(data=self.data)

        X_train, X_test, y_train, y_test = train_test_split(processed_data, test_size=0.2)
        self.model.endog = X_train
        self.model.fit()

        start_date = len(X_train)
        end_date = start_date + len(y_train)
        self.preds = self.model.predict(start=start_date, end=end_date)

        return self

    @classmethod
    def spas_name(cls):
        return 'arima_model'
