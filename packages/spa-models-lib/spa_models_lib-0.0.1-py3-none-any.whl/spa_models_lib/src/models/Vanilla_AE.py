from ssl import SSLSyscallError
from turtle import shape
import tensorflow as tf
from keras.models import Model
from keras.layers import Dense, Input
# from keras.regularizers import L1L2
from keras import regularizers
from tensorflow.keras.callbacks import ModelCheckpoint
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
import keras

from tensorflow.keras.models import Model as ModelK
from tensorflow.python.keras.saving import saving_utils

class Model(ModelK):

  def __reduce__(self):
    model_metadata = saving_utils.model_metadata(self)
    training_config = model_metadata.get("training_config", None)
    model = self.to_json()
    weights = self.get_weights()
    return (self.unpack, (model, training_config, weights))

  @staticmethod
  def unpack(model, training_config, weights):
      restored_model = keras.models.model_from_json(model)
      restored_model.set_weights(weights)
      return restored_model    

class Vanilla_AE(SPA_models):

  def build_new(self, input_shape: Tuple, *args, **kwargs) -> None:

    self.input_shape = input_shape
    # self.weights = model_weights
    # self.threshold = threshold
    # self.error_weights = param_weights

    self.input_layer = Input(shape = (self.input_shape[1]))

    self.encoder_l1 = Dense(10, activation='elu',
                kernel_initializer='glorot_uniform',
                # kernel_initializer='ones',
                # kernel_initializer='zeros',
                kernel_regularizer=regularizers.l2(0.0))(self.input_layer)

    self.emded_layer = Dense(2,
                kernel_initializer='glorot_uniform',
                # kernel_initializer='ones',
                # kernel_initializer='zeros'
                )(self.encoder_l1)

    self.decoder_l1 = Dense(10, 
                kernel_initializer='glorot_uniform',
                # kernel_initializer='ones',
                # kernel_initializer='zeros',
                )(self.emded_layer)

    self.output_layer = Dense(self.input_shape[1],
                kernel_initializer='glorot_uniform',
                # kernel_initializer='ones',
                # kernel_initializer='zeros',
                )(self.decoder_l1)

    self.model = Model(inputs = self.input_layer, outputs = self.output_layer)

            
  def build_exist(self, input_shape: Tuple,  model_config: Dict, model_object, model_weights: List, threshold = float, param_weights: List = [], *args, **kwargs):
    
    self.input_shape = input_shape
    self.threshold = threshold
    self.error_weights = param_weights

    if model_object:
       self.model = model_object
    else:  
      self.model = Model.from_config(model_config)
      self.model.set_weights(model_weights)


    

  def calc(self, data: npt.NDArray):

    dates = data[:, 0]
    data = data[:, 1:].astype('float')

    predict_out = self.model.predict(data) 
    self.model_error = np.abs(predict_out - data) #* self.error_weights
    self.mean_model_error = np.c_[dates, np.mean(self.model_error, axis=1)]
    self.status = np.c_[dates, np.array(self.mean_model_error[:, 1:] >= self.threshold).astype(int)]
    keras.backend.clear_session()
    # test = Data(name = 'integral_value',
    #          points =  [Point(d = value[0].isoformat(), v = value[1] ) for value in self.mean_model_error])

    calc_out = namedtuple('calc', ['error', 'status'])

    return calc_out(self.mean_model_error, self.status)

  def train(self, trainX: npt.NDArray, trainY: npt.NDArray,
          BATCH_SIZE = 10, validation_split = 0.2, EPOCHS = 20):
     
    trainX =  trainX[:, 1:].astype('float')
    trainY  = trainY[:, 1:].astype('float')

    self.model.compile(optimizer = keras.optimizers.Adam(learning_rate=0.001), loss = 'mae')

    #ModelCheckpoint(#"best_model.h5", 
                            #monitor = 'val_loss',
                            #save_best_only = True,
                            #mode = 'min',
                            #verbose = 0),
    callbacks=[DWELL(model = self.model, monitor_acc = False, factor=.95, verbose=False)]

    history = self.model.fit(trainX, trainY,
                        batch_size = BATCH_SIZE,
                        epochs=EPOCHS,
                        callbacks=callbacks,
                        validation_split=validation_split,
                        verbose=0,
                        use_multiprocessing = True)
 

    train_pred = self.model.predict(trainX)
    train_error = np.abs(train_pred - trainY)
    self.error_weights = 1 / (np.mean(train_error, axis=0) / np.mean(train_error, axis=0).sum())
    self.error_weights = self.error_weights / sum(self.error_weights)
    self.threshold = np.quantile(a=np.mean(train_error, axis=1), q=0.999) #*self.error_weights
    self.weights = self.model.get_weights()
    self.model_config = self.model.get_config()
    keras.backend.clear_session()
    # np.mean(np.abs(X_pred-X_train_scaled), axis = 1)
    # dict(zip(feature_names, error_contrib[0]))
    # Train = namedtuple('train', ['train_data', 'threshold', 'weights'])
    return self

  def contribs(self, data:npt.NDArray):

    abs_error = np.abs(self.model_error)
    error_contrib = np.divide(abs_error, np.sum(abs_error, axis=1).reshape(-1, 1))
    error_contrib = np.c_[data[:, 0], error_contrib]
    
    return error_contrib

  def linear_forecast(self, data: npt.NDArray) -> float:
      
    # линейный прогноз срабатывания модели, дата пересечения тренда с порогом

    win_size_hist = 151 # окно для обучения модели (сутки) 10 минутных значений
    win_size_pred = 4320 # окно для предсказания модели (месяц) 10 минутных значений (6*24*30)

    data.insert(0, self.mean_model_error[0][1])
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
      X_test_scaled =  np.c_[data[:, 0], self.scaler.transform(data[:, 1:])]


      # train/test split
      splitted_data = namedtuple('splitted_data', ['trainX', 'trainY', 'testX', 'testY'] )


      return splitted_data(X_train_scaled, X_train_scaled, X_test_scaled, X_test_scaled)
