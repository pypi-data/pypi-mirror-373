from typing import Any, Union

import numpy as np
import pandas as pd
from sklearn.preprocessing import MinMaxScaler
from sklearn.utils.validation import check_is_fitted
from tsquared import HotellingT2

from spa_models_lib.src.anomalies_detection.base import MultivariateModels


class Hotelling_T2(MultivariateModels):
    """
    Класс для обучения и предсказания аномальных значений с помощью статистической модели Хотеллинга на основе библиотеки [tsquared](https://github.com/cetic/tsquared).
    """


    MODEL_TYPE = 'MULTIVARIATE_ANOMALY'
    
    def get_model(
        self, threshold: Union[float, int] = None, model_object: Any = None, scaler_object=None, *args, **kwargs
    ):
        
        """
        Метод, в котором устанавливаются модель, пороговое значение для обнаружения аномалий и объект для скалирования данных

        Аргументы:
        threshold: Union[float, int] = None: пороговое значение для обнаружения аномалий, которое определяет, что считать аномалией;
        model_object: объект модели, которая будет использоваться для обнаружения аномалий;
        scaler_object: объект масштабирования данных;
        """

        self.model = model_object
        self.anomaly_threshold = threshold
        self.scaler_object = scaler_object

    def __setup_model(self, hotelling_alpha: float = 0.005):

        """
        Метод, инициализирующий модель HotellingT2 с указанным значением уровня значимости (alpha)

        Аргументы:
        hotelling_alpha: float = 0.005: уровень значимости
        """

        self.model = HotellingT2()
        self.model.alpha = hotelling_alpha

    def __setup_data(self, data: pd.DataFrame, training=False, *args: Any, **kwargs: Any):

        """
        Метод, масштабирующий данные в зависимости от того, выполняется ли обучение или происходит расчет на уже обученной модели

        Алгоритм:
        1. проверка условия обучения; 
        2. если условие False, то данные масшитабируются с использованием ранее созданного объекта scaler_object, после чего возвращаются нормированные данные;
        3. если условие True, то создается новый объект scaler_object класса MinMaxScaler

        Аргументы:
        data: pd.DataFrame: исходные данные
        training: bool = False: флаг обучения
        *args: Any: любые другие параметры
        **kwargs: Any: любые другие ключевые параметры

        Возврат:
        scaled_data: нормированные данные (в зависимости от того, какой флаг установлен у Training)
        """

        if training == False:
            scaled_data = self.scaler_object.transform(data.values)
            return scaled_data

        elif training == True:
            self.scaler_object = MinMaxScaler()
            scaled_data = self.scaler_object.fit_transform(data)
            return scaled_data

    def fit(self, data: pd.DataFrame):

        """
        Метод, обучающий модель

        Алгоритм:
        1. вызывается метод __setup_data(data, training=True), который создает нормированные данные;
        2. метод __setup_model() инициализирует модель;
        3. метод fit() обучает модель;
        4. метод __get_threshold() вычисляет пороговое значение;
        5. метод __get_contribs() вычисляет веса ошибок;
        6. метод __get_anomaly_status() вычисляет статус аномалий;

        Аргументы:
        data: pd.DataFrame: исходные данные
        """

        self.data = data
        processed_data = self.__setup_data(data=self.data, training=True)
        self.__setup_model()
        self.model.fit(processed_data)
        self.anomaly_threshold = 1
        self.error_weights = np.ones(data.values.shape[1])
        self.model_object = self.model
        # self.__get_threshold(processed_data)
        return self

    def predict(self, data: pd.DataFrame):

        """
        Метод для предсказания аномалий на новых данных.

        Алгоритм:
        1. вызывается метод __setup_data(data, training=False), который создает нормированные данные;
        2. определение количества образцов (n) из атрибута модели n_samples_in_;
        3. применение метода score_samples() модели к нормированным данным;
        4. вычисление верхнего контрольного предела (ucl), интегральной ошибки и статуса аномалий;
        5. метод __get_contribs() вычисляет веса ошибок;

        Возврат:
        preds: np.array: предсказания аномалий
        """

        self.data = data
        processed_data = self.__setup_data(data=self.data, training=False)
        n = self.model.n_samples_in_
        self.preds = self.model.score_samples(processed_data)
        self.ucl = n / (n + 1) * self.model.ucl_indep_
        self.integral_error = pd.Series(data=np.log10(self.preds / self.ucl), index=self.data.index)
        self.anomaly_status = pd.Series(
            data=(self.integral_error.values >= self.anomaly_threshold).astype(int), index=self.data.index
        )
        self.__get_contribs(data=processed_data)
        return self.preds

    def fit_predict(self):
        ...

    def __get_contribs(self, data: np.array):

        """
        Метод для вычисления вкладов в аномалии на основе обработанных данных.

        Алгоритм:
        1. метод __myt_decomposition() вычисляет вклады в аномалии;
        2. вычисление суммарного вклада по каждому признаку;
        3. создается датафрейм, в котором каждый элемент равен отношению вклада к суммарному вкладу;

        Аргументы:
        data: np.array: нормированные данные
        """

        myt_values = self.__myt_decomposition(data)
        sum_contrib_t2 = np.sum(myt_values, axis=1)
        self.anomaly_contribs = pd.DataFrame(
            data=np.divide(myt_values, sum_contrib_t2.reshape(-1, 1)), index=self.data.index, columns=self.data.columns
        )

    def __myt_decomposition(self, data):

        """
        Метод для вычисления вкладов в аномалии на основе обработанных данных.

        Алгоритм:
        1. проверяется, что модель обучена;
        2. высчитывается ковариационная матрица за исключением признака j;
        3. применяется метод np.linalg.pinv() для вычисления обратной матрицы;
        4. обработка итоговых значений для исключения NaN и бесконечностей.

        Аргументы:
        data: данные для декомпозиции

        Возврат:
        myt_values: np.array: вклады в аномалии    
        """

        check_is_fitted(self.model)
        data = self.model._check_test_inputs(data)
        n_samples, n_features = data.shape

        data_cent = data - self.model.mean_
        s_squared = np.empty(n_features)
        data_bar = np.empty((n_features, n_samples))

        for j in range(n_features):
            sxx = np.delete(self.model.cov_[j], j)
            b_j = np.linalg.pinv(np.delete(np.delete(self.model.cov_, j, axis=1), j, axis=0)) @ sxx

            s_squared[j] = self.model.cov_[j, j] - sxx @ b_j
            data_bar[j] = self.model.mean_[j] + np.delete(data_cent, j, axis=1) @ b_j

        myt_values = (data - data_bar.T) ** 2 / s_squared

        myt_values[np.isnan(myt_values)] = 0.0
        myt_values[np.isinf(myt_values)] = 0.0

        return myt_values

    @classmethod
    def spas_name(cls):
        return 'Hotelling_T2'
