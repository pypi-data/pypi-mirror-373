from datetime import datetime, timedelta, timezone
import numpy as np
import numpy.typing as npt
import pandas as pd
from sklearn.linear_model import LinearRegression
from spa_models_lib.src.ts_forecasting.base import ForecastingOutputs, TSForecasting


class TrendModel(TSForecasting):
    def __init__(self, winsize_hist: str, threshold: float = None, *args, **kwargs):
        """
        Метод, реализующий инициализацию модели LinearRegression.

        Аргументы:
        winsize_hist: str: размер окна предсказания;
        threshold: float: пороговое значение для определения аномалий;
        *args, **kwargs: дополнительные аргументы для инициализации.
        """

        self.threshold_alarm = threshold
        self.model = LinearRegression(n_jobs=-1)

    def fit(self, series: pd.Series):
        """
        Метод, реализующий обучение модели.

        Алгоритм:
        1. приведение индексов временного ряда к формату даты и времени;
        2. округления временных индексов до ближайшей минуты;
        3. перерасчет временного ряда на интервал с шагом 1 минута;
        4. подгонка модели к полученному ряду.

        Аргументы:
        series: pd.Series: временной ряд для обучения
        """
        self.series = series
        self.series.index = pd.to_datetime(series.index)
        self.series.index = self.series.index.round('min')
        self.series_resampled = self.series.copy()
        self.series_resampled = self.series_resampled.resample('60000ms', kind='timestamp').interpolate('linear')
        self.model.fit(
            self.series_resampled.index.astype(np.int64).values.reshape(-1, 1),
            self.series_resampled.values.reshape(-1, 1),
        )

        return self

    def predict(self, series: pd.Series, **kwargs):
        """
        Метод, реализующий предсказание на основе обученной модели.

        Алгоритм:
        1. приведение индексов временного ряда к формату даты и времени;
        2. применение обученной модели для предсказания значений временного ряда;
        3. преобразание результатов в объект Series с использованием индексов временного ряда.

        Аргументы:
        series: pd.Series: временной ряд для предсказания;
        **kwargs: дополнительные аргументы для настройки предсказания.

        Возврат:
        predictions: pd.Series: предсказанный ряд.    
        """

        series.index = pd.to_datetime(series.index)
        results = self.model.predict(series.index.astype(np.int64).values.reshape(-1, 1))
        self.predictions = pd.Series(data=results.reshape(1, -1)[0], index=series.index)
        return self.predictions

    def forecast(self, series: pd.Series, horizon: str = '30D', frequency_data: str = '1min', **kwargs):
        """
        Метод, реализцющий прогнозирование на основен обученной модели.

        Алгоритм:
        1. приведение индексов временного ряла к формату даты и времени;
        2. вычисление времени первого и последнего индексов для прогноза на основе указанного периода и частоты;
        3. подготовка данных для прогноза, добавляя пустое значение для последней даты прогноза;
        4. применение обученной модели для прогноза;
        5. преобразование результатов в объект Series с использованием индексов временного ряда.

        Аргументы:
        series (pd.Series): временной ряд для прогнозирования
        horizon (str): прогнозируемый период:
        frequency_data (str): частота данный временного ряда;
        **kwargs: дополнительные аргументы для настройки прогнозирования.

        Возврат:
        forecasts: pd.Series: прогнозируемый ряд.
        """
        
        series.index = pd.to_datetime(series.index)
        first_forecast_idx = self.series.index[-1].to_pydatetime() + pd.Timedelta(frequency_data)
        last_forecast_idx = self.series.index[-1].to_pydatetime() + pd.Timedelta(horizon)
        prepared_data = self.series._append(pd.Series(data=[np.nan], index=[last_forecast_idx]))
        prepared_data = prepared_data.resample(frequency_data, kind='timestamp').interpolate('linear')
        results = self.model.predict(prepared_data.index.astype(np.int64).values.reshape(-1, 1))
        forecasted_series = pd.Series(data=results.reshape(1, -1)[0], index=prepared_data.index)
        self.date_prediction_unix = 0.0
        if self.threshold_alarm:
            self.forecasts = forecasted_series.loc[first_forecast_idx:].copy()
            alarm_data = self.forecasts[self.forecasts > self.threshold_alarm]
            try:
                self.date_prediction = alarm_data.index[0]   # первая дата пересечения порога
                self.date_prediction_unix = int(datetime.timestamp(alarm_data.index[0].replace(tzinfo = timezone.utc)))      # первая дата пересечения порога в unix
                
            except IndexError:
                pass
        return self.forecasts

    def fit_predict(self, series: pd.Series, **kwargs):
        """
        Метод, реализующий обучение и предсказание на основе обученной модели.

        Алгоритм:
        1. приведение индексов временного ряда к формату даты и времени;
        2. обучение модели;
        3. предсказание значений временного ряда.

        Аргументы:
        series (pd.Series): временной ряд для обучения и предсказания;
        **kwargs: дополнительные аргументы для настройки обучения и предсказания.

        Возврат:
        predictions (pd.Series): предсказанный ряд.
        """

        series.index = pd.to_datetime(series.index)
        self.fit(series)
        self.predict(series)
        return self.predictions
