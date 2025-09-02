from typing import Any
import pandas as pd
from sklearn.cluster import KMeans as KMeans_model
from sklearn.preprocessing import MinMaxScaler
from spa_models_lib.src.anomalies_detection.base import MultivariateModels


class KMeans(MultivariateModels):
    """
    Класс, реализующий алгоритм кластеризации KMeans для выявления многомерных аномалий.
    """

    MODEL_TYPE = 'MULTIVARIATE_ANOMALY'

    def __setup_model(
        self, n_clusters: int, n_init=int, *args: Any, **kwargs: Any
    ) -> None:
        """
        Метод, инициализирующий модель KMeans.

        Аргументы:
        n_clusters (int): количество кластеров;
        n_init (int): количество итераций;
        *args, **kwargs: дополнительные аргументы.
        """

        self.model = KMeans_model(
            n_clusters=n_clusters, random_state=7, n_init=n_init
        )

    def __setup_data(self, data: pd.DataFrame, *args: Any, **kwargs: Any):
        """
        Метод, инициализирующий нормализацию данных.

        Алгоритм:
        1. Создание объекта MinMaxScaler;
        2. Исходные данные масштабируются с помощью fit_transform;
        3. Нормализованные данные возвращаются в виде DataFrame.

        Аргументы:
        data (pd.DataFrame): исходные данные;
        *args, **kwargs: дополнительные аргументы.

        Возврат:
        scaled_data (pd.DataFrame): нормализованные данные
        """

        self.scaler_object = MinMaxScaler()
        scaled_data = self.scaler_object.fit_transform(data)
        scaled_data = pd.DataFrame(
            scaled_data, columns=data.columns, index=data.index
        )
        return scaled_data

    def fit_predict(self, data: pd.DataFrame, min_norm_duration: float=1):
        """
        Метод для обучения и прогнозирования.

        Алгоритм:
        1. Обработка исходных данных с помощью __setup_data;
        2. Настройка модели KMeans с помощью __setup_model;
        3. Прогнозирование с помощью fit_predict;
        4. Идентификация кластеров (нормальный/аномальный);
        5. Фильтрация аномалий с помощью _filter.

        Аргументы:
        data (pd.DataFrame): исходные данные.
        """

        self.data = data
        processed_data = self.__setup_data(data=self.data)

        self.__setup_model(n_clusters=2, n_init=5)
        self.preds = pd.Series(
            self.model.fit_predict(processed_data),
            index=processed_data.index.to_list(),
        )
        self.anomaly_status = self._identify(self.preds, self.data)
        self.anomaly_status_filtered = self._duration_filter(
            self._indents_filter(self.anomaly_status, indent_duration=144), 
            min_norm_duration=min_norm_duration * 144
            )

    def _identify(self, classification, df):
        """
        Метод для идентификации кластеров (нормальный/аномальный).

        Алгоритм:
        1. Если доля аномалий > 0.5, то инвертировать классификацию;
        2. Если доля аномалий = 0.5, то идентификация кластеров по std средних значений тегов;
        3. Если std для 0 больше, чем для 1, то инвертировать классификацию.

        Аргументы:
        classification (pd.Series): предсказания модели;
        df (pd.DataFrame): исходные данные.

        Возврат:
        classification (pd.Series): Series с однозначной классификацией.
        """

        if classification.mean() > 0.5:
            classification = 1 - classification
        elif classification.mean() == 0.5:
            df['classification'] = classification
            std_norm = df[df['classification'] == 0.].drop(columns=['classification']).mean().std()
            std_anom = df[df['classification'] == 1.].drop(columns=['classification']).mean().std()
            if std_norm > std_anom:
                classification = 1 - classification
                std_norm, std_anom = std_anom, std_norm
        return classification

    def _indents_filter(self, classif: pd.Series, indent_duration=144):
        # алгоритм работает только с непрерывными временными рядами, а здесь передается рад без офлайн-участков, 
        # поэтому непрерывный ниже создается вручную
        classification = pd.Series(index=pd.date_range(classif.index[0], classif.index[-1], freq='10min')).fillna(1)
        classification.loc[classif.index] = classif
        # границы участков
        delta = classification - classification.shift().fillna(0)
        # начало аномалии
        begin = delta[delta == 1]
        # конец аномалии
        end = delta[delta == -1]
        # если конец аномалии - последний элемент, то вручную добавляем его индекс
        if len(begin) > len(end):
            end.loc[classification.index[-1]] = 0
        classification_filtered = classification.copy()
        classification_filtered.loc[:] = 0
        # заполнение аномалий с отступами
        for anom_begin, anom_end in zip(begin.index.to_list(), end.index.to_list()):
            indent_begin = anom_begin - pd.Timedelta(f'{(indent_duration)*10}m')
            indent_end = anom_end + pd.Timedelta(f'{(indent_duration-1)*10}m')
            classification_filtered.loc[indent_begin : indent_end] = 1
        return classification_filtered.loc[classif.index]
    
    def _duration_filter(self, classif: pd.Series, min_norm_duration=144):
        # алгоиртм работает только с непрерывными временными рядами, а здесь передается ряд без офлайн-участков, 
        # поэтому ниже создается непрерывный вручную
        classification = pd.Series(index=pd.date_range(classif.index[0], classif.index[-1], freq='10min')).fillna(1)
        classification.loc[classif.index] = classif
        # границы участков
        delta = classification - classification.shift().fillna(1)
        # начало нормы
        begin = delta[delta == -1]
        # конец нормы
        end = delta[delta == 1]
        # если конец нормы - последний элемент, то вручную добавляем его индекс
        if len(begin) > len(end):
            end.loc[classification.index[-1] + pd.Timedelta(f'{10}m')] = 0
        classification_filtered = classification.copy()
        classification_filtered.loc[:] = 1
        # заполнение нормальных участков длительностью больше 24 ч
        for norm_begin, norm_end in zip(begin.index.to_list(), end.index.to_list()):
            if norm_end - norm_begin >= pd.Timedelta(f'{min_norm_duration*10}m'):
                classification_filtered.loc[norm_begin : norm_end - pd.Timedelta(f'{10}m')] = 0
        return classification_filtered.loc[classif.index]
        
    def fit():
        pass

    def predict():
        pass

    @classmethod
    def spas_name(cls):
        return 'KMeans'
