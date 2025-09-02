import numpy as np
import pandas as pd
from math import isclose
from spa_models_lib.src.anomalies_detection.base import UnivariateModels


class FreezingDetector(UnivariateModels):
    """
    Класс для обнаружения замораживания (залипания) одномерных аномалий.
    """

    MODEL_TYPE = 'UNIVARIATE_ANOMALY'

    def __init__(self, freezing_count: int = 5, rel_tol: float = 1e-9, *args, **kwargs):
        """
        Метод с инициализацией количества последних изменений, которые должны быть одинаковыми для определения замораживания (залипания).

        Аргументы:
        freezing_count (int): число замораживания (залипания);
        *args, **kwargs: дополнительные аргументы.
        """
        self.freezing_count = 5 if freezing_count is None else freezing_count
        self.rel_tol = rel_tol

    def predict(self, series: pd.Series):
        """
        Метод, реализующий прогнозирование на основе обученной модели.

        Алгоритм:
        1. сортировка временного ряда по индексу;
        2. проверка условия равенства средних значений последних freezing_count значений последней точке из этого периода:
            2.1 если условие выполняется, то аномалия;
            2.1 если условие не выполняется, то нет аномалии.
        
        Аргументы:
        series (pd.Series): временной ряд для предсказания.

        Возврат:
        anomaly_status (int): статус аномалии.
        """

        series.sort_index(inplace=True)

        if (
            np.all(series[-self.freezing_count - 1 :].map(lambda x: isclose(series[-self.freezing_count - 1 :].mean(), x, rel_tol=self.rel_tol)))
            and len(series) >= self.freezing_count
        ):
            self.anomaly_status = 1
        else:
            self.anomaly_status = 0

        return self.anomaly_status   # AnomaliesOutputs(**self.__dict__)

    def fit(self):
        pass

    def fit_predict(self):
        pass

    # для СПАС
    @classmethod
    def spas_name(cls):
        return 'stick'
