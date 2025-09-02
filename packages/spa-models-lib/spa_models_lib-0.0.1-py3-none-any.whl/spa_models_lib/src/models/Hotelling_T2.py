from sklearn.linear_model import LinearRegression
from dateutil import parser
from spa_models_lib.src.models.BaseModule import SPA_models
from spa_models_lib.src.models.DynamicLR import DWELL
from datetime import timedelta, datetime
import numpy as np
from collections import namedtuple
from sklearn.preprocessing import StandardScaler, MinMaxScaler
from typing import Tuple, List, Dict
import numpy.typing as npt
from tsquared import HotellingT2


class Hotelling_T2(SPA_models):

    def build_new(self, *args, **kwargs) -> None:

        self.model = HotellingT2()
        self.model.alpha = 0.005

    def build_exist(self, threshold, model_object, *args, **kwargs):

        self.model = model_object
        self.threshold = threshold
        
    # def build(self, weights: List = [], *args, **kwargs) -> None:
        
    #     self.model = HotellingT2()
    #     self.model.alpha = 0.005
    #     self.weights = weights

    #     if self.weights:
    #         self.model.cov_ = weights[0]
    #         self.model.mean_ = weights[1]
    #         self.model.ucl_indep_ = weights[2]
    #         self.model.n_features_in_ = weights[3]
    #         self.model.n_samples_in_ = weights[4]
        
    def calc(self, data: npt.NDArray):

        dates = data[:, 0]
        data = data[:, 1:].astype('float')

        n = self.model.n_samples_in_
        # t2_model_out = self.model.score_samples(data.reshape(1, -1))
        t2_model_out = self.model.score_samples(data)
        ucl = n / (n + 1) * self.model.ucl_indep_
        self.error = np.c_[dates, np.log10(t2_model_out / ucl)]
        
        self.status = np.c_[dates, np.array(self.error[:, 1:] >= self.threshold).astype(int)]

        calc_out = namedtuple('calc', ['error', 'status'])

        return calc_out(self.error, self.status)


    def train(self, trainX: npt.NDArray, trainY = None):

        trainX =  trainX[:, 1:].astype('float')
        self.model.fit(trainX)
        self.threshold = 1

        # cov_ = self.model.cov_
        # mean_ = self.model.mean_
        # ucl_indep_ = self.model.ucl_indep_
        # n_features_in_ = self.model.n_features_in_
        # n_samples_in_ = self.model.n_samples_in_
        self.error_weights = np.ones(trainX.shape[1])

        # n = self.model.n_samples_in_
        # t2_model_out = self.model.score_samples(trainX)[0]
        # ucl = n / (n + 1) * self.model.ucl_indep_

        # self.t2_log_value = np.log10(t2_model_out / ucl)
        # self.weights = [self.model.cov_, self.model.mean_, self.model.ucl_indep_,  self.model.n_features_in_, self.model.n_samples_in_] # веса
        # import shutil
        # import base64
        # import io
        # import zipfile
        # import pickle
        # pickle.dump(t2_weights, open('model_weights.pkl', 'wb'))
        # with open('t2_weights.zip', 'rb') as f:
        #     bytes = f.read()
        #     encoded = base64.b64encode(bytes)
        # with open('t2_weights.txt', 'wb') as f:
        #     f.write(encoded)
        return self


    def contribs(self, data:npt.NDArray):
        dates = data[:, 0]
        data = data[:, 1:].astype('float')
        

        # conditional_t2_terms = self.myt_decomposition(data[0].reshape(1, -1))
        conditional_t2_terms = self.__myt_decomposition(data)
        sum_contrib_t2 = np.sum(conditional_t2_terms, axis=1)
        normalized_contribs_t2 = np.c_[dates, np.divide(conditional_t2_terms, sum_contrib_t2.reshape(-1, 1))]
        # out_contribs = dict(zip(feature_names, normalized_contribs_t2[0]))

        return normalized_contribs_t2

    def linear_forecast(self, data: npt.NDArray) -> float:
      
        # линейный прогноз срабатывания модели, дата пересечения тренда с порогом

        win_size_hist = 151 # окно для обучения модели (сутки) 10 минутных значений
        win_size_pred = 1100*3 # окно для предсказания модели (неделя) 10 минутных значений

        data.insert(0, self.error[0][1])
        X_values = np.arange(1,win_size_hist+win_size_pred+1).reshape(-1, 1)

        reg = LinearRegression(n_jobs=-1).fit(X_values[:win_size_hist], data)

        pred_new = reg.predict(X_values[win_size_hist:win_size_hist+win_size_pred+1])

        date_intersection = 0.0

        if self.status[0][1] != 1:
            for i in range(win_size_pred):

                if pred_new[i] >= self.threshold:
                    date_intersection = datetime.utcnow() + timedelta(minutes=10*(i+1)) # дата пересечения с threshold
                    date_intersection = datetime.timestamp(date_intersection)
                    break

        return date_intersection    

    def data_preproc(self, data: npt.NDArray, periods: Dict = None, scaler_object = None, training = False, *args, **kwargs):
    
        if training == False:
            self.scaler = scaler_object
            self.scaled_data = np.c_[data[:, 0], self.scaler.transform(data[:, 1:])]
            return self.scaled_data

        elif training == True:
            filtered_data = np.empty(shape=[0, data.shape[-1]])
            if periods.Normal:
                for train_period in periods.Normal:
                    start_period = parser.parse(train_period.begin) #datetime.strptime(train_period.Item1, '%Y-%m-%dT%H:%M')
                    end_period = parser.parse(train_period.end) #datetime.strptime(train_period.Item12, '%Y-%m-%dT%H:%M')
                    cond = np.logical_and(data[:, 0]>=start_period, data[:,0]<=end_period)
                    filtered_data = np.append(filtered_data, data[cond, :], axis=0)
        else:
            filtered_data = data

        # скалирование
        self.scaler = StandardScaler()
        X_train_scaled = np.c_[filtered_data[:, 0], self.scaler.fit_transform(filtered_data[:, 1:])] 
        X_test_scaled =  np.c_[data[:, 0], self.scaler.fit_transform(data[:, 1:])]


        # train/test split
        splitted_data = namedtuple('splitted_data', ['trainX', 'trainY', 'testX', 'testY'] )


        return splitted_data(X_train_scaled, X_train_scaled, X_test_scaled, X_test_scaled)

    
    def __myt_decomposition(self, data):
        from sklearn.utils.validation import check_is_fitted
        check_is_fitted(self.model)
        data = self.model._check_test_inputs(data)
        n_samples, n_features = data.shape
        
        data_cent = data - self.model.mean_
        s_squared = np.empty(n_features)
        data_bar = np.empty((n_features, n_samples))
        
        for j in range(n_features):
            sxx = np.delete(self.model.cov_[j], j)
            b_j = np.linalg.pinv(
                    np.delete(np.delete(self.model.cov_, j, axis=1), j,
                            axis=0)
            ) @ sxx
            
            s_squared[j] = self.model.cov_[j, j] - sxx @ b_j
            data_bar[j] = self.model.mean_[j] + \
                    np.delete(data_cent, j, axis=1) @ b_j
            
        myt_values = (data-data_bar.T) ** 2 / s_squared
        
        myt_values[np.isnan(myt_values)] = 0.
        myt_values[np.isinf(myt_values)] = 0.
        
        return myt_values
