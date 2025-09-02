import tensorflow as tf
from keras.models import Model
from keras.layers import LSTM
from keras.layers import Flatten
from keras.layers import Bidirectional
from keras.layers import Dense, Input
from keras.layers import Lambda
from keras.regularizers import L1L2
from keras.layers import RepeatVector
from keras.layers import TimeDistributed
from tensorflow.keras.callbacks import ModelCheckpoint
import numpy as np
import pandas as pd
# from nested_lookup import nested_lookup
from sklearn.linear_model import LinearRegression
import os
import sys
import json
from dateutil.parser import parse
import logging
from typing import Dict, List
# sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from spa_models_lib.src.models.BaseModule import SPA_models
# from schema import schema
from spa_models_lib.src.models.DynamicLR import DWELL


class LSTM_AE(SPA_models):

    # def __new__(cls, *args, **kwargs):
    #     cls.input_params = kwargs
    #     return super().__new__()

    def build(self, *args, **kwargs):

        self.input_params = kwargs
        # super(SPA_models, self).g(*args, **kwargs)
        # self.input_shape = input_shape

        self.input_layer = Input(shape = (self.input_params['input_shape'][0], self.input_params['input_shape'][1]))

        self.input_encoder_l1 =  Bidirectional(LSTM(64,  recurrent_dropout = 0.2, return_sequences = True,
                                                    kernel_regularizer = L1L2(l1 = 0.01, l2=0.01)))(self.input_layer)

        self.input_encoder_l2 = Bidirectional(LSTM(32, recurrent_dropout = 0.2, return_sequences = True))(self.input_encoder_l1)

        #for_reconstruction
        self.recons_decoder_l1 = tf.keras.layers.AveragePooling1D(pool_size=self.input_params['input_shape'][0])(self.input_encoder_l2)

        self.recons_decoder_l2 = Flatten()(self.recons_decoder_l1)

        self.recons_decoder_l3 = RepeatVector(self.input_params['input_shape'][0])(self.recons_decoder_l2)

        self.recons_decoder_l4 = Bidirectional(LSTM(32, return_sequences = True,
                                    recurrent_dropout = 0.2))(self.recons_decoder_l3)

        self.recons_decoder_l5 = Bidirectional(LSTM(64, return_sequences = True,
                                    recurrent_dropout = 0.2))(self.recons_decoder_l4)

        self.recons_out_layer = TimeDistributed(Dense(self.output_shape[0][1], activation = 'linear'), name = 'reconstruction')(self.recons_decoder_l5)

        #for_prediction
        self.predict_decoder_l1 = Lambda(lambda t:[t, t[:, -1, :]])(self.input_encoder_l2) 

        self.predict_decoder_l2 = RepeatVector(self.input_params['input_shape'][0])(self.predict_decoder_l1[1])

        self.predict_decoder_l3 = Bidirectional(LSTM(32, return_sequences = True, recurrent_dropout = 0.2))(self.predict_decoder_l2)

        self.predict_decoder_l4 = Bidirectional(LSTM(64, return_sequences = True,
                                    recurrent_dropout = 0.2))(self.predict_decoder_l3)

        self.predict_out_layer = TimeDistributed(Dense(self.output_shape[1][1], activation = 'linear'), name = 'prediction')(self.predict_decoder_l4)

        self.model = Model(inputs = self.input_layer, outputs = [self.recons_out_layer, self.predict_out_layer])

        if getattr(self.input_params, 'weights'):
            self.model.set_weights(self.input_params['weights'])
            
        if getattr(self.input_params, 'threshold'):
            self.threshold = self.input_params['threshold']


    def predict(self, data) -> List:
        return self.model.predict(data)

    def calc(self, data):
        return None

    def train(self, data, BATCH_SIZE = 10, validation_split = 0.2, EPOCHS = 15):

        self.model.compile(optimizer = tf.keras.optimizers.Nadam(),
                            loss = {'prediction':'MSE', 'reconstruction': tf.keras.metrics.mean_absolute_error})

        callbacks=[ModelCheckpoint("best_model_LSTM.h5", monitor = 'val_loss', save_best_only = True, mode = 'min', verbose = 1),
                                    DWELL(model = self.model, monitor_acc = False, factor=0.9, verbose=True)]

        self.model = self.model.fit(data['trainX'], data['trainY_recon'], data['trainY_pred'],
                            batch_size= BATCH_SIZE,
                            epochs = EPOCHS, callbacks = callbacks,
                            validation_split=validation_split, verbose = 0, use_multiprocessing = True)
        return self.model

    async def contribs(self):
        pass

    async def data_preproc(self, df, training = False, **kwargs): 

        if not training:
            pass
        # преобразование входных данных в метки с 10-ти минутными интервалами
        bool_tags = [self.data.inputs[i].name for i in range(df.shape[1]) if self.data.inputs[i].props.isBool == True and self.data.inputs[i].i!= 999 and self.data.inputs[i].i!= 900]
        # not_bool_tags = [self.data.inputs[i].name for i in range(df.shape[1]) if self.data.inputs[i].props.isBool == True and self.data.inputs[i].i!= 999 and self.data.inputs[i].i!= 900]

        for col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
        
        # ресемплинг по 1 секунде, заполнение пустых значений последними доступными данными
        df = df.resample("1s").first().fillna(method = 'ffill')
            
        df.dropna(inplace=True)

        # для булевых тэгов
        df_bool = df[bool_tags]
        df_bool = df_bool.rolling(600, min_periods=1, step = 600).median()

        # числовые тэги
        df_numeric = df.drop(bool_tags, axis=1)
        df_numeric = df_numeric.rolling(600, min_periods=1, step = 600).mean()

        df = pd.concat([df_bool, df_numeric], axis=1)

        # standard mode, усреднение по 10 минут
        # df = df.rolling(600, min_periods=1, step = 600).mean()

        return df