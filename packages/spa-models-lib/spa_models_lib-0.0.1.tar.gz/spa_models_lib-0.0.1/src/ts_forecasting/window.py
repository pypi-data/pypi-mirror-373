import pandas as pd
from datetime import timedelta
import json
import numpy as np
from spa_models_lib.src.ts_forecasting.base import TSForecasting

class WindowAlgorithm(TSForecasting):
    """
    Класс оконного алгоритма для прогнозирования данных
    """

    def __init__(self, window_size: int=20):
      """
      Метод инициализации размера окна

      Аргументы:
      window_size (int): размер окна
      """

      self.window_size = window_size

    def fit(self, data: pd.Series):
      """
      Метод обучения данных

      Алгоритм:
      1. Исходные данные обрезаются до размера window_size;
      2. Полученное окно данных делится пополам, у каждой половины берется среднее;
      3. Высчитывается дельта как разность средних двух половин.

      Аргументы:
      data (pd.Series): исходные данные
      """

      data = data[-self.window_size:]
      length = len(data)
      half_length = length // 2
      mean_first_half = np.mean(data[:half_length])
      mean_second_half = np.mean(data[half_length:-1])
      self.delta = mean_second_half - mean_first_half

    def forecast(self, data: pd.Series, horizon: int=10):
      """
      Метод прогнозирования данных

      Алгоритм:
      1. Определяется индекс фактического (по которому и будет проводится прогноз) значение - это последний элемент окна;
      2. Формирование прогнозного значения:
          2.1. Индекс равен индексу фактического значения + значение горизонта, за которое брать прогноз;
          2.2. Значение прогнозна равно фактическому значению + дельта, полученная в методе fit.

      Аргументы:
      data (pd.Series): исходные данные
      horizon (int): горизонт прогноза

      Возврат:
      forecast_value: прогнозное значение
      """

      fact_index = data.index[-1]
      forecast_index = fact_index + timedelta(minutes=10*horizon)
      forecast_value = pd.Series(data.loc[fact_index] + self.delta, index=[forecast_index])
      return forecast_value

    def fit_predict():
      pass

    def predict():
      pass