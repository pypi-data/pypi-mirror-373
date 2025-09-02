from typing import Any, Dict, List, Tuple, Union
import keras
import numpy as np
import pandas as pd
import tensorflow as tf
from keras.layers import Input
from keras.layers import Bidirectional
from keras.layers import LSTM
from keras.regularizers import L1L2
from keras.layers import AveragePooling1D
from keras.layers import Flatten
from keras.layers import RepeatVector
from keras.layers import TimeDistributed
from keras.layers import Dense
from keras.layers import Lambda
from keras.models import Model
from keras.models import load_model
from tensorflow.keras.callbacks import ModelCheckpoint
from sklearn.preprocessing import MinMaxScaler
from tensorflow.keras.models import Model as ModelKeras
from tensorflow.python.keras.saving import saving_utils
from spa_models_lib.src.anomalies_detection.base import MultivariateModels
from spa_models_lib.src.anomalies_detection.Multivariate.autoencoders.dynamicLR import DWELL

class Model(ModelKeras):
    """
    Кастомный класс для сохранения модели в pickle, а затем в бинарник.
    """

    def __reduce__(self):
        """
        Метод, использующий Pickle для сериализации объекта.

        Возврат:
        (self.unpack, (model, training_config, weights)): функция для десериализации объекта и данные, необходимые для воссоздания объекта: 
        модель, конфигурацию обучения и веса модели
        """

        model_metadata = saving_utils.model_metadata(self)
        training_config = model_metadata.get('training_config', None)
        model = self.to_json()
        weights = self.get_weights()
        return (self.unpack, (model, training_config, weights))

    @staticmethod
    def unpack(model, training_config, weights):
        """
        Статический метод, который распаковывает модель из JSON-строки, конфигурацию обучения, устанавливает веса для этой модели. 
        Затем восстановленная модель возвращается в качестве результата.
 
        Аргументы:
        model (str): строка JSON, представляющая модель.
        training_config (dict): конфигурация для обучения модели.
        weights (список): веса, которые необходимо установить для модели.
 
        Возврат:
        restored_model: восстановленная модель.
        """

        restored_model = keras.models.model_from_json(model)
        restored_model.set_weights(weights)
        return restored_model


class LSTM_AutoEncoder(MultivariateModels):
    """
    Класс для обучения и предсказания модели LSTM Autoencoder для обнаружения многомерных аномалий.
    """

    MODEL_TYPE = 'MULTIVARIATE_ANOMALY'

    def get_model(self,
        model_config: Dict = None,
        model_weights: List = None,
        threshold: Union[float, int] = None,
        model_object: Any = None,
        weighted_errors: bool = True,
        error_weights: list = None,
        scaler_object=None,
        *args,
        **kwargs
    ):
        """
        Получение модели для обнаружения многомерных аномалий (MULTIVARIATE_ANOMALY).

        Алгоритм:
        1. устанавливается объект масштабирования данных и пороговое значение для обнаружения аномалий;
        2. модель задается как объект или конфиг модели и веса;
        3. если не получилось создать модель, то возвращает исключение.

        Аргументы:
        model_config: Dict = None: конфигурация модели в виде словаря
        model_weights: List = None: веса модели в виде списка
        threshold: Union[float, int] = None: пороговое значение для обнаружения аномалий
        model_object: Any = None: существующий объект модели (если есть)
        scaler_object = None: объект масштабирования данных
        *args: любые другие аргументы
        **kwargs: любые другие ключевые аргументы
        """

        self.scaler_object = scaler_object
        self.anomaly_threshold = threshold
        self.weighted_errors = weighted_errors
        self.error_weights = error_weights

        try:
            if model_object:
                self.model = model_object

            elif model_config and model_weights:
                try:
                    self.model = Model.from_config(model_config)
                except:
                    self.model = keras.Sequential.from_config(model_config)
                self.model.set_weights(model_weights)
            else:
                raise ValueError('Cannot create model instance due to problems with models configurations')
        except:
            raise ValueError('Cannot create model instance due to problems with models configurations')

    def __setup_model(self, input_shape: Tuple, *args: Any, **kwargs: Any) -> None:
        """
        Метод, инициализирующий модель нейронной сети для LSTM Autoencoder.

        Алгоритм:
        1. задается форма входных данных, в данном случае это кортеж, первый элемент которого обозначает количество признаков во входных данных;
        2. создание входного слоя, где форма слоя равна форме входных данных;
        3. последовательно создаются два слоя Bidirectional LSTM для кодирования информации в self.encoder;
        4. в self.decoder1 и self.decoder2 выполняются операции декодирования данных;
        5. создаются слои LSTM, RepeatVector, TimeDistributed и Dense для сжатия и восстановления данных;
        6. создается модель с помощью объекта Model из библиотеки Keras, где входным слоем является self.input_layer, а выходами являются self.decoder1 и self.decoder2, которые представляют восстановленные данные и прогнозы соответственно.

        Аргументы:
        input_shape: Tuple: форма входных данных
        *args, **kwargs: Any: любые другие ключевые параметры
        """

        # TODO: расширить входные параметры

        self.input_shape = input_shape
        self.input_layer = Input(shape=(self.input_shape))

        self.encoder =  Bidirectional(LSTM(64,  recurrent_dropout = 0.2, return_sequences = True,
                                kernel_regularizer = L1L2(l1 = 0.01, l2=0.01)))(self.input_layer)
        self.encoder = Bidirectional(LSTM(32, recurrent_dropout = 0.2, return_sequences = True))(self.encoder)
        
        self.decoder1 = AveragePooling1D(pool_size=input_shape[0])(self.encoder)
        self.decoder1 = Flatten()(self.decoder1)
        self.decoder1 = RepeatVector(input_shape[0])(self.decoder1)
        self.decoder1 = Bidirectional(LSTM(32, return_sequences = True,
                                recurrent_dropout = 0.2))(self.decoder1)
        self.decoder1 = Bidirectional(LSTM(64, return_sequences = True,
                                recurrent_dropout = 0.2))(self.decoder1)
        self.decoder1 = TimeDistributed(Dense(input_shape[1], activation = 'linear'), 
                                name = 'reconstruction')(self.decoder1)

        self.decoder2 = Lambda(lambda t:[t, t[:, -1, :]])(self.encoder) 
        self.decoder2 = RepeatVector(input_shape[0])(self.decoder2[1])
        self.decoder2 = Bidirectional(LSTM(32, return_sequences = True, recurrent_dropout = 0.2))(self.decoder2)
        self.decoder2 = Bidirectional(LSTM(64, return_sequences = True,
                                recurrent_dropout = 0.2))(self.decoder2)
        self.decoder2 = TimeDistributed(Dense(input_shape[1], activation = 'linear'), 
                                name = 'prediction')(self.decoder2)

        self.model = Model(inputs=self.input_layer, outputs = [self.decoder1, self.decoder2])

    def check_seq(self, data):
        """
        Метод для проверки последовательности временных меток и постоянства временного шага в DataFrame.

        Алгоритм:
        1. инициализация первой временной метки в данных;
        2. создание списка для проверки последовательности временных меток;
        3. цикл по каждой временной метке в данных, используя enumerate для получения индекса и временной метки;
        4. первая временная метка сравнивается с первой временной меткой;
        5. если разница между текущей и предыдущей временной меткой больше 10 минут, то текущей временной метке присваивается False;
        6. создание нового столбца в DataFrame с именем check_time и добавление его в список check_time.

        Аргументы:
        data (pd.DataFrame): DataFrame с временными метками
        
        Возврат:
        data: DataFrame с добавленным столбцом check_time
        """

        first = data.index[0]
        check_time = []
        for index, time in enumerate(data.index):
            diff = time - first
            if index == 0:
                check = True
            elif diff > pd.Timedelta("10min"):
                check = False
            else: 
                check = True
            first = time
            check_time.append(check)
        data['check_time'] = check_time
        return data

    def to_sequences(self, data_x: pd.DataFrame, data_y: pd.DataFrame, history_size=10, prediction_size=10):
        """
        Метод для создания последовательностей данных для обучения и прогнозирования.

        Алгоритм:
        1. проверка последовательности временных меток входных и выходных данных с помощью метода check_seq;
        2. создание пустых списков x_values, y_values_prediction, y_values_reconstruction и index_cur_time, в которые будут добавляться последовательности входных данных, прогнозов и реконструкций, а также соответствующие временные метки;
        3. цикл по индексам данных с учетом history_size и prediction_size;
        4. проверяется условие, что все объекты, необходимые для расчета текущей временной метки, идут последовательно и с одинаковым временным шагом;
        5. при выполнении условия создаются переменные для хранения исторических, прогнозных и реконструкций последовательностей;
        6. данные добавляются в соответствующие списки;
        7. добавляется текущая временная метка в списке index_cur_time.

        Аргументы:
        data_x (pd.DataFrame): DataFrame с входными данными
        data_y (pd.DataFrame): DataFrame с выходными данными
        history_size (int): кол-во периодов, на которое мы смотрим "назад"
        prediction_size (int): кол-во периодов, на которое мы прогнозируем

        Возврат:
        index_cur_time (list): список временных меток
        x_values (np.array): тренировочные последовательности данных
        y_values_reconstruction (np.array): реконструкции тренировочных последовательностей
        y_values_prediction (np.array): прогнозы тренировочных последовательностей
        """

        x = self.check_seq(data_x)
        y = self.check_seq(data_y)
        x_values = []
        y_values_prediction = []
        index_cur_time = []
        
        for i in range(len(x)-history_size-prediction_size+1):
            if x.iloc[i+1 : i+history_size+prediction_size, -1].mean() == 1:
                input_x = x.iloc[i:(i+history_size), :-1] 
                x_values.append(input_x)
                y_pred = y.iloc[i+history_size : (i+history_size + prediction_size), :-1] 
                y_values_prediction.append(y_pred)
                index_cur_time.append(x.index[i+history_size+prediction_size-1])
            else:
                continue
                
        return index_cur_time, np.array(x_values), np.array(y_values_prediction)
    
    def to_pred_sequences(self, x: pd.DataFrame, y: pd.DataFrame, history_size=10, prediction_size=10):
        # history_size - кол-во периодов, на которое мы смотрим "назад"
        # prediction_size - кол-во периодов, на которое мы прогнозируем
        x_values = []
        y_values_prediction = []
        index_cur_time = []
        
        for i in range(len(x)-history_size-prediction_size+1):
            input_x = x.iloc[i:(i+history_size), :] 
            x_values.append(input_x)
            y_pred = y.iloc[i+history_size : (i+history_size + prediction_size), :] 
            y_values_prediction.append(y_pred)
            index_cur_time.append(x.index[i+history_size+prediction_size-1])

        return index_cur_time, np.array(x_values), np.array(y_values_prediction)
    
    def __setup_data(self, data: pd.DataFrame, training=False, *args: Any, **kwargs: Any):
        """
        Метод, масштабирующий данные в зависимости от того, выполняется ли обучение или происходит расчет на уже обученной модели.

        Алгоритм:
        1. проверка условия обучения;
        2. если условие False, то формируется DataFrame с данными, которые масштабируются с использованием ранее созданного объекта scaler_object, столбцы и индексы соответствуют исходным данным;
        3. если условие True, то создается новый объект scaler_object класса MinMaxScaler и формируется DataFrame с масштабированными данными с помощью fit_transform, столбцы и индексы соответствуют исходным данным.
        
        Аргументы:
        data: pd.DataFrame: исходные данные
        training (bool): флаг обучения
        *args, **kwargs: Any: любые другие параметры

        Возврат:
        self.to_sequences(scaled_data, scaled_data): результат работы вызова метода to_sequences, передавая ему масштабированны данные scaled_data (они передаются в качестве входных и выходных данных)
        """

        if training == False:

            scaled_data = pd.DataFrame(self.scaler_object.transform(data.values), columns=data.columns, index=data.index)
            return self.to_pred_sequences(scaled_data, scaled_data)

        elif training == True:

            self.scaler_object = MinMaxScaler()
            scaled_data = pd.DataFrame(self.scaler_object.fit_transform(data), columns=data.columns, index=data.index)
            return self.to_sequences(scaled_data, scaled_data)

    def fit(self, data: pd.DataFrame, BATCH_SIZE=10, validation_split=0.2, EPOCHS=10, weighted_errors: bool = False, error_weights: list = None):
        """
        Метод обучения модели.

        Алгоритм:
        1. вызывается метод __setup_data для масштабирования данных;
        2. вызывается метод __setup_model для создания модели;
        3. компиляция модели с помощью метода compile и выбранными оптимизатором и функцией потерь;
        4. обучение модели на масштабированных данных;
        5. расчет прогноза;
        6. расчет реконструкций;
        7. вычисление разницы между прогнозом и масштабированными данными;
        8. вычисление разницы между реконструкцией и масштабированными данными;
        9. вычисление интегральной ошибки;
        10. определение порога аномалий с помощью метода __get_threshold;
        11. определение важности признаков с помощью метода __get_contribs;
        12. формирование pd.Series со статусом аномалий. 

        Аргументы:
        data: pd.DataFrame: исходные данные
        BATCH_SIZE (int): размер батча
        validation_split (float): доля данных для валидации
        EPOCHS (int): количество эпох

        Возврат:
        self: объект класса
        """

        self.data = data
        index_cur_time_train, trainX, trainY_pred = self.__setup_data(data=self.data, training=True)

        self.weighted_errors = weighted_errors

        self.__setup_model(input_shape=(trainX.shape[1], trainX.shape[2]))

        self.model.compile(optimizer = tf.keras.optimizers.Nadam(),
              loss = {'prediction':'MSE', 
                      'reconstruction': tf.keras.metrics.mean_absolute_error})
        callbacks = [DWELL(model=self.model, monitor_acc=False, factor=0.9, verbose=False)]

        self.model.fit(
            trainX, 
            [trainX, trainY_pred],
#            batch_size=BATCH_SIZE,
            epochs=EPOCHS,
            callbacks=callbacks,
            validation_split=validation_split,
            verbose=0,
            use_multiprocessing=True,
        )

        _train_recons, train_predict  = self.model.predict(trainX)
        train_recons, _train_predict  = self.model.predict(trainY_pred)
        keras.backend.clear_session()

        # resids_recons = np.average(abs(train_recons - trainY_pred), axis =1)
        # resids_predict = np.mean(abs(train_predict  - trainY_pred)**2, axis = 1)
        # self.__get_param_weights(resids_recons, resids_predict)

        resids_recons = np.average(abs(train_recons - trainY_pred), weights = np.arange(1, 11, 1), axis =1)
        resids_predict = np.average(abs(train_predict  - trainY_pred)**2, axis =1)
        resids = pd.DataFrame((resids_recons + resids_predict)/2, 
                               index=index_cur_time_train, 
                               columns=data.columns)
        self.resids = pd.DataFrame(index=data.index)
        self.resids[data.columns] = resids[data.columns]

        self.__get_contribs()
        self.__calc_weights()

        self.integral_error = self.__calc_integral_error()
        
        self.__get_threshold()

        self.resids = self.resids.fillna(0)
        self.integral_error = self.integral_error.fillna(0)
        
        self.anomaly_status = pd.Series(
            data=self.integral_error > self.anomaly_threshold, index=self.integral_error.index
        ).astype(int)

        self.model_weights = self.model.get_weights()
        self.model_config = self.model.get_config()

        self.model_object = self.model

        return self   # AnomaliesOutputs.from_dict(self.__dict__)

    # def __get_param_weights(self, resids_recons, resids_predict):
        # расчет весов
        # тут объединяются смещенные по индексам ошибки по реконс и предс только для весов
        # error_train = resids_recons + resids_predict
        # errors_train = pd.DataFrame(error_train, columns=self.data.columns)
        
        # error_weight = 1/(errors_train.mean()/errors_train.mean().sum())
        # self.error_weight = error_weight/sum(error_weight)

    def __calc_weights(self):
        self.error_weights = 1 / self.resids.std()
        self.error_weights = (self.error_weights - self.error_weights.min()) * 0.5 + self.error_weights.min()
        self.error_weights = self.error_weights / self.error_weights.sum()

    def __calc_integral_error(self, weights=None):
        if self.weighted_errors:
            weights = self.error_weights
        return pd.Series(data=np.average(a=self.resids, axis=1, weights=weights), index=self.resids.index)

    def __get_threshold(self):
        """
        Метод для вычисления порогового значения.

        Алгоритм:
        1. удаляются пропуски из интегральной ошибки;
        2. использование метода quantile для определения порога аномалий.
        """

        self.anomaly_threshold = np.quantile(self.integral_error.dropna(), q=0.997)

    def predict(self, data: pd.DataFrame):
        """
        Метод для прогнозирования аномалий на основе обученных данных.

        Алгоритм:
        1. вызов метода __setup_data для предварительной обработки данных;
        2. формирование входных данных для модели и получения индекса текущего времени;
        3. расчет прогноза;
        4. расчет реконструкций;
        5. расчет и усреднение ошибок реконструкции и прогнозирования;
        6. формирование DataFrame суммарной усредненной ошибки расчета, индексированных по времени;
        7. если количество строк DataFrame меньше или равно удвоенному размеру входных данных X, удаляются строки с отсутствующими значениями;
        8. расчет интегральной ошибки;
        9. вызов метода __get_contribs для вычисления вклада признаков;
        10. пропущенные значения в DataFrame и интегральной ошибки заполеяются нулями;
        11. создание серии со статусом аномалий.

        Аргументы:
        data (pd.DataFrame): исходные данные
        """

        self.data = data
        index_cur_time, X, Y_pred = self.__setup_data(data=self.data, training=False)
        _recons, predict = self.model.predict(X)
        recons, _predict = self.model.predict(Y_pred)

        resids_recons = np.average(abs(recons - Y_pred), weights = np.arange(1, X.shape[1]+1, 1), axis =1)
        resids_predict = np.average(abs(predict - Y_pred)**2, axis =1)

        resids = pd.DataFrame((resids_recons + resids_predict)/2, 
                                   index=index_cur_time, 
                                   columns=data.columns)
        self.resids = pd.DataFrame(index=data.index)
        self.resids[data.columns] = resids[data.columns]

        if self.resids.shape[0] <= X.shape[1]*2:
            self.resids = self.resids.dropna()
        
        self.integral_error = self.__calc_integral_error()
        
        self.__get_contribs()

        self.resids = self.resids.fillna(0)
        self.integral_error = self.integral_error.fillna(0)

        self.anomaly_status = pd.Series(
            data=self.integral_error > self.anomaly_threshold, index=self.integral_error.index
        ).astype(int)
        
        keras.backend.clear_session()

    def fit_predict(self, data: pd.DataFrame, BATCH_SIZE=10, validation_split=0.2, EPOCHS=20):

        self.fit(data=pd.DataFrame, BATCH_SIZE=BATCH_SIZE, validation_split=validation_split, EPOCHS=EPOCHS)
        self.model.predict(data)
        return self.preds

    def __get_contribs(self):
        """
        Метод для вычисления вкладов признаков.

        Алгоритм:
        Определяется вклад параметра, как отношениее частной ошибки параметра к общей ошибки автоэнкодера в данной временной метке
        """    

        a_values = self.resids.values
        b_values = np.sum(self.resids.values, axis=1).reshape(-1, 1)
        error_contrib = np.divide(a_values, b_values,where=b_values!=0,out=np.zeros_like(a_values))
        self.anomaly_contribs = pd.DataFrame(data=error_contrib, index=self.resids.index, columns=self.data.columns).fillna(0)

    @classmethod
    def spas_name(cls):
        return 'LSTM_AutoEncoder'