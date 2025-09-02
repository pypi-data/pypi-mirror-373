import numpy as np
import pandas as pd

from spa_models_lib.src.anomalies_detection.base import UnivariateModels


class OutliersDetector(UnivariateModels):
    """
    Класс для обнаружения одномерных аномалий.
    """

    MODEL_TYPE = 'UNIVARIATE_ANOMALY'

    def __init__(
        self,
        outlier_sensity: str = 'medium',
        hi_percent: float = 0.95,
        low_percent: float = 0.05,
        bound_coef: int = 5,
        statistic_len: int = 144,
        statistic_len_for_mean: int = 12,
        *args,
        **kwargs
    ):
        """
        Инициализация класса обнаружения выбросов.

        Аргументы:
        outlier_sensity (str): параметр чувствительности;
        bound_coef (int): коэффициент для порога;
        hi_percent (float): высший порог перцентиля;
        low_percent (float): низший порог перцентиля;
        statistic_len (int): длина записи статистики (из идеи 1 расчет в 10 минут);
        statistic_len_for_mean (int): длина статистики для расчета среднего значения.
        """

        self.outlier_sensity = (
            'medium' if outlier_sensity is None else outlier_sensity
        )
        self.bound_coef = bound_coef if bound_coef is None else bound_coef
        if self.outlier_sensity == 'low':
            self.bound_coef = 10
        elif self.outlier_sensity == 'medium':
            self.bound_coef = 7
        elif self.outlier_sensity == 'high':
            self.bound_coef = 5

        self.hi_percent = hi_percent
        self.low_percent = low_percent
        self.statistic_len = statistic_len
        self.statistic_len_for_mean = statistic_len_for_mean

    def predict(
        self,
        series: pd.Series,
        statistic: pd.Series = None,
        last_point: pd.Timestamp = None,
    ):
        """
        Метод для обнаружения выбросов.

        Аргументы:
        series (pd.Series): входные данные для расчета выбросов;
        statistic (pd.Series): история значений для расчета статистики;
        last_point (pd.Timestamp): предыдущая последняя точка, которая была в расчете.
        """

        series = series.groupby(series.index).last()
        if statistic is None or statistic.empty:
            statistic = series.iloc[:-1]
            last_point = series.index[-2]

        normalized_series = statistic[
            (statistic <= statistic.quantile(self.hi_percent))
            * (statistic >= statistic.quantile(self.low_percent))
        ]
        if len(normalized_series) < 2:
            normalized_series = statistic
        week_std = normalized_series.std()
        mean = np.mean(normalized_series.iloc[-self.statistic_len_for_mean :])

        hi_bound = mean + self.bound_coef * week_std
        low_bound = mean - self.bound_coef * week_std

        points_to_check = series.loc[last_point:].iloc[:-1]
        prev_diff = (points_to_check - series.shift(1)).dropna()
        next_diff = (series.shift(-1) - points_to_check).dropna()

        outlier_status = points_to_check[
            prev_diff[
                ((prev_diff).abs() > self.bound_coef * week_std)
                & ((prev_diff) * (next_diff) < 0)
                & (
                    (points_to_check >= hi_bound)
                    + (points_to_check <= low_bound)
                )
            ].index
        ]
        if outlier_status.any():
            self.anomaly_status = 1
        else:
            self.anomaly_status = 0
        if not (statistic is None or statistic.empty):
            # new_points = points_to_check.drop(
            #     index=outlier_status.index, errors='ignore'
            # )
            new_points = points_to_check.copy()
            new_points.drop_duplicates(inplace=True)
            try:
                if statistic[-1] == new_points[0]:
                    new_points.drop(new_points.index[0], inplace=True)
            except IndexError:
                pass
            statistic = pd.concat([statistic, new_points])
            statistic = statistic.iloc[-self.statistic_len :]
        last_point = series.index[-1]

        statistic = statistic.groupby(statistic.index).last()

        return self.anomaly_status, statistic, last_point

    def fit(self):
        pass

    def fit_predict(self):
        pass

    @classmethod
    def spas_name(cls):
        return 'outlier'
