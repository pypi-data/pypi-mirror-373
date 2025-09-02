import numpy as np
import pandas as pd
from spa_models_lib.src.anomalies_detection.base import UnivariateModels


class TrendDetector(UnivariateModels):
    """
    Класс для обнаружения трендов в одномерных данных.
    """

    MODEL_TYPE = 'UNIVARIATE_ANOMALY'

    def __init__(self,
        trend_sensity: str = 'medium',
        hi_percent: float = 0.95,
        low_percent: float = 0.05,
        bound_coef: int = 5,
        statistic_len: int = 144,
        statistic_len_for_mean: int = 12,
        *args,
        **kwargs
    ):
        """
        Инициализация класса обнаружения лавинной скорости.

        Аргументы:
        trend_sensity (str): параметр чувствительности;
        bound_coef (int): коэффициент для порога;
        hi_percent (float): высший порог перцентиля;
        low_percent (float): низший порог перцентиля;
        statistic_len (int): длина записи статистики (из идеи 1 расчет в 10 минут);
        statistic_len_for_mean (int): длина статистики для расчета среднего значения.
        """

        self.trend_sensity = (
            'medium' if trend_sensity is None else trend_sensity
        )
        self.bound_coef = bound_coef if bound_coef is None else bound_coef
        if self.trend_sensity == 'low':
            self.bound_coef = 10
        elif self.trend_sensity == 'medium':
            self.bound_coef = 7
        elif self.trend_sensity == 'high':
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
        Метод обнаруженя лавинной скорости.

        Аргументы:
        series (pd.Series): входные данные для расчета выбросов;
        statistic (pd.Series): история значений для расчета статистики;
        last_point (pd.Timestamp): предыдущая последняя точка, которая была в расчете.

        Алгоритм "лавинная скорость":
        1. На вход подается 2-х часовое окно сырых данных
        2. Производится проверка условий. Лавинная скорость отмечается, когда выполняются все 3 условия: <br>
            1) предпоследняя точка сильно отклоняется от предыдущей точки - с учетом временных интервалов
            2) последняя точка отклоняется в ту же сторону от предпоследней - без учета временных интервалов
            3) (
                предпоследняя точка сильно отклоняется от среднего - без учета временных интервалов
                или
                последняя точка сильно отклоняется от предыдущей точки - с учетом временных интервалов
            )
        Возврат:
        anomaly_status (int): статус аномалии.
        """

        series = series.groupby(series.index).last()
        if statistic is None or statistic.empty:
            statistic = series.iloc[:-1]
            last_point = series.index[-2]

        # std разностей без учета временных интервалов
        # вычисляем разности в статистике
        statistics_diff = (statistic - statistic.shift(1)).dropna().abs()
        # отсекаем разности по квантилям и считаем std
        diff_std = statistics_diff[(statistics_diff <= statistics_diff.quantile(self.hi_percent)) * (statistics_diff >= statistics_diff.quantile(self.low_percent))].std()
        
        # std разностей с учетом временных интервалов
        # делим разности в статистике на временные интервалы
        statistics_diff_scaled = statistics_diff / ((statistic.index[1:] - statistic.index[:-1]).seconds / 60)
        # отсекаем разности по кванитлям (без учета временных интервалов)
        statistics_diff_scaled = statistics_diff_scaled[(statistics_diff <= statistics_diff.quantile(self.hi_percent)) * (statistics_diff >= statistics_diff.quantile(self.low_percent))]
        # считаем std
        diff_std_scaled = statistics_diff_scaled.std()
        
        clear_statistics = statistic[(statistic <= statistic.quantile(self.hi_percent)) * (statistic >= statistic.quantile(self.low_percent))]
        week_std = clear_statistics.std()
        self.mean = np.mean(clear_statistics.iloc[-12:])

        new_points = series.loc[last_point:].iloc[1:]

        points_to_check = series.loc[last_point:].iloc[1:]
        diff = (series - series.shift(1)).dropna() / ((series.index[1:] - series.index[:-1]).seconds / 60)
        prev_diff = diff.shift(1).dropna()

        # пересечение для всех трех: diff, prev_diff, points_to_check
        index_to_check = points_to_check.index.intersection(diff.index).intersection(prev_diff.index)
        diff = diff[index_to_check]
        prev_diff = prev_diff[index_to_check]
        points_to_check = points_to_check[index_to_check]

        cond_1 = (prev_diff).abs() > self.bound_coef * diff_std_scaled
        cond_2 = (prev_diff) * (diff) > 0
        cond_3 = ((points_to_check - self.mean).abs() > self.bound_coef * diff_std) + (diff.abs() > self.bound_coef * diff_std_scaled)
        
        speed_status = points_to_check[cond_1 & cond_2 & cond_3]

        if speed_status.any():
            self.anomaly_status = 1
        else:
            self.anomaly_status = 0

        if not (statistic is None or statistic.empty):
            # new_points = points_to_check.drop(
            #     index=speed_status.index, errors='ignore'
            #     )
            new_points = points_to_check.copy()
            new_points.drop_duplicates(inplace=True)
            try:
                if statistic[-1] == new_points[0]:
                    new_points.drop(new_points.index[0], inplace=True)
            except IndexError:
                pass
            statistic = pd.concat([statistic, new_points])
            statistic = statistic.iloc[-self.statistic_len:]
        last_point = series.index[-1]

        statistic = statistic.groupby(statistic.index).last()

        return self.anomaly_status, statistic, last_point

    def fit(self):
        pass

    def fit_predict(self):
        pass

    @classmethod
    def spas_name(cls):
        return 'velocity'
