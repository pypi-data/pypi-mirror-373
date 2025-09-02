from typing import Any
import pandas as pd
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
from pyod.models.iforest import IForest
from pyod.models.mcd import MCD
from pyod.models.inne import INNE
from pyod.models.rod import ROD
from spa_models_lib.src.anomalies_detection.base import MultivariateModels


class PYOD(MultivariateModels):
    """
    Класс, реализующий алгоритм PyOD, предназначенный для обнаружения многомерных аномалий.
    """

    MODEL_TYPE = 'MULTIVARIATE_ANOMALY'

    def __setup_data(self, data: pd.DataFrame, *args: Any, **kwargs: Any):
        """
        Метод для стандартизации данных.

        Алгоритм:
        1. Создание объекта StandardScaler;
        2. Использования fit_transform для стандартизации данных;
        3. Создание нового DataFrame с нормализованными данными.

        Аргументы:
        data (pd.DataFrame): исходные данные (вместе с офлайном);
        *args, **kwargs: дополнительные аргументы.

        Возврат:
        scaled_data (pd.DataFrame): нормализованные данные
        """

        self.scaler_object = StandardScaler()
        scaled_data = self.scaler_object.fit_transform(data)
        scaled_data = pd.DataFrame(
            scaled_data, columns=data.columns, index=data.index
        )
        return scaled_data

    def fit_predict(self, data: pd.DataFrame):
        """
        Метод для обучения и прогнозирования.

        Алгоритм:
        1. Вызов метода __setup_data для стандартизации данных для исходных данных;
        2. Использования PCA для уменьшения размерности данных;
        3. Формирования нового DataFrame с нормализованными данными, имена столбцов которого сгенерированы на основе результатов PCA;
        4. Вызов метода __setup_data для стандартизации данных уже для нового DataFrame;
        5. Инициализация классификаторов;
        6. Создание пустого DataFrame с именами столбцов, соответствующими именам классификаторов и индексами из df_pca;
        7. Для каждого классификатора обучается модель и вычисляется оценка решения для каждого элемента заданного набора данных;
        
        Аргументы:
        data (pd.DataFrame): исходные данные;

        Возврат:
        pd.concat([df_pca, df_pyod], axis=1): объединенные DataFrame, содержащие полученные признаки и оценки решения на заданном наборе данных.
        """

        self.data = data
        processed_data = self.__setup_data(data=self.data)

        pca = PCA(n_components=0.99, random_state=12345)
        df_pca = pca.fit_transform(processed_data)
        col_names = ['tag_'+str(i+1) for i in range(pca.n_components_)]
        df_pca = pd.DataFrame(df_pca,
                              columns=col_names,
                              index=processed_data.index)
        df_pca = self.__setup_data(data=df_pca)


        classifiers = {'IF': IForest(contamination=0.3, random_state=12345),
                       'MCD': MCD(contamination=0.3, random_state=12345),
                       'INNE': INNE(contamination=0.3, random_state=12345),
                       'ROD': ROD(contamination=0.3)}
        df_pyod = pd.DataFrame(columns=list(classifiers.keys()),
                               index=df_pca.index.to_list())
        for clf_name, clf in classifiers.items():
            clf.fit(df_pca)
            series_pyod = pd.Series(clf.decision_scores_,
                                    index=df_pyod.index)
            df_pyod[clf_name] = series_pyod

        return pd.concat([df_pca, df_pyod], axis=1)

    def fit():
        pass

    def predict():
        pass

    @classmethod
    def spas_name(cls):
        return 'Pyod'
