from typing import Any
import pandas as pd
from spa_models_lib.src.anomalies_detection.base import MultivariateModels
from ruptures import BottomUp
from tsfresh import extract_features
from tsfresh.utilities.dataframe_functions import impute
from tsfresh.feature_extraction.settings import MinimalFCParameters
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans


class BottomUp_kmeans(MultivariateModels):
    """
    Класс, реализующий алгоритм сегментации Bottom-up и формирования признаков tsfresh
    """

    MODEL_TYPE = 'MULTIVARIATE_ANOMALY'

    def fit_predict(self, data: pd.DataFrame, offline_index=None, min_norm_duration: float=1):
        """
        Метод для обучения и прогнозирования.

        Аргументы:
        data (pd.DataFrame): результат работы моделей PyOD на исходных данных.
        """

        self.data = data
        self.offline_index = offline_index
        self.min_norm_duration = min_norm_duration

        self.model = BottomUp(model='l2', min_size=144 * self.min_norm_duration).fit(data)
        self.bkps = self.model.predict(n_bkps=len(data) / 432)

        tsfresh_df = self.make_tsfresh_df()
        tsfresh_df = self.clear_segments(tsfresh_df)
        tsfresh_features = self.extract_tsfeatures(tsfresh_df)
        tsfresh_features = self.sacling(tsfresh_features)
        kmeans_pred = self.clustering(tsfresh_features)
        tsfresh_df = self.arrange_clusters(tsfresh_df, kmeans_pred)
        self.clusters = self.separate_clusters(tsfresh_df, self.data, kmeans_pred)


    def make_tsfresh_df(self):
        """
        Метод для разметки сегментов и формирования датафрейма 
        по шаблону tsfresh.
        """
        tsfresh_df = pd.DataFrame(columns=['id', 'datetime'] + self.data.columns.to_list())
        bkps_1 = [0] + self.bkps

        for i, end in enumerate(self.bkps):
            begin = bkps_1[i]
            segment = self.data.iloc[begin:end,:].reset_index(names='datetime')
            segment['id'] = i
            tsfresh_df = pd.concat([tsfresh_df, segment])
        return tsfresh_df


    def clear_segments(self, tsfresh_df):
        """
        Метод для удаления офлайна из сегментов и слишком коротких сегментов
        """
        # Удаление офлайна из сегментов
        tsfresh_df_online = tsfresh_df.set_index('datetime')[~self.offline_index]
        # Удаление сегментов короче 24ч
        segments_len = tsfresh_df_online.groupby(by='id')[tsfresh_df.columns[-1]].count()
        short_segments = segments_len[segments_len < 144].index.to_list()
        tsfresh_df_online = tsfresh_df_online[tsfresh_df_online['id'].apply(lambda x: x not in short_segments)]
        tsfresh_df_online.reset_index(drop=False, inplace=True, names='datetime')
        return tsfresh_df_online
    

    def extract_tsfeatures(self, data):
        settings = MinimalFCParameters()
        ts_features = extract_features(
            data, 
            column_id='id', 
            column_sort='datetime',
            impute_function=impute, 
            default_fc_parameters=settings,
            n_jobs=6,
            disable_progressbar=True,
            show_warnings=False
            )
        return ts_features
    

    def sacling(self, tsfresh_features_reduced):
        tsfresh_features_reduced_scaled = pd.DataFrame(
            StandardScaler().fit(tsfresh_features_reduced).transform(tsfresh_features_reduced),
            columns=tsfresh_features_reduced.columns, 
            index=tsfresh_features_reduced.index
            )
        return tsfresh_features_reduced_scaled
    

    def clustering(self, tsfresh_features_reduced_scaled):
        kmeans = KMeans(n_clusters=4, random_state=42, n_init=5)
        kmeans_pred = pd.Series(kmeans.fit_predict(tsfresh_features_reduced_scaled),index=tsfresh_features_reduced_scaled.index)
        return kmeans_pred


    def arrange_clusters(self, df, kmeans_pred):
        tsfresh_df_online = df.copy()
        tsfresh_df_online['clust'] = None
        for i in kmeans_pred.index.to_list():
            tsfresh_df_online['clust'].where(tsfresh_df_online['id'] != i, other=kmeans_pred.loc[i], inplace=True)
        return tsfresh_df_online
    

    def separate_clusters(self, tsfresh_df_online, X_test, kmeans_pred):
        clusters = pd.DataFrame(index=X_test.index, columns=kmeans_pred.unique())
        for cluster in clusters.columns:
            clusters.loc[tsfresh_df_online[tsfresh_df_online['clust'] == cluster]['datetime'], cluster] = 1
        clusters = clusters.fillna(0)
        return clusters
        
    def fit():
        pass

    def predict():
        pass

    @classmethod
    def spas_name(cls):
        return 'KMeans'
