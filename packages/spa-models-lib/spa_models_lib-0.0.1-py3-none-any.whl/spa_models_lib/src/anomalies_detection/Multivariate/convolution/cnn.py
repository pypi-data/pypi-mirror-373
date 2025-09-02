from typing import Any, Dict, List, Tuple, Union
import keras
import numpy as np
import pandas as pd
import tensorflow as tf
from keras.models import Sequential
from keras.layers import Dense
from keras.layers import Flatten
from keras.layers import Dropout
from keras.layers import Conv1D
from sklearn.preprocessing import StandardScaler
from sklearn.utils import shuffle
from tensorflow.keras.models import Model as ModelKeras
from tensorflow.python.keras.saving import saving_utils
from tensorflow.keras.layers import Input
from spa_models_lib.src.anomalies_detection.base import MultivariateModels
from spa_models_lib.src.anomalies_detection.Multivariate.autoencoders.dynamicLR import DWELL


class Model(ModelKeras):
    """
    Кастомный класс для сохранения модели в pickle, а затем в бинарник
    """

    def __reduce__(self):
        """
        метод, использующий Pickle для сериализации объекта.

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


class CNN(MultivariateModels):
    """
    Класс сверточной нейронной сети (CNN).
    """

    MODEL_TYPE = 'MULTIVARIATE_ANOMALY'

    def get_model(self,
        model_object: Any = None,
        scaler_object=None,
        threshold: Union[float, int] = None,
        *args,
        **kwargs
    ):
        """
        Метод, создающий модель, пороговое значение для обнаружения аномалий и объект стандартизации данных.

        Аргументы:
        model_object: объект модели
        scaler_object: объект стандартизатора
        threshold: порог аномалий
        *args и **kwargs: другие аргументы
        """

        self.scaler_object = scaler_object
        self.anomaly_threshold = threshold

        try:
            self.model = model_object
        except:
            raise ValueError('Cannot create model instance due to problems with models configurations')

    def __setup_model(self, input_shape: Tuple, *args: Any, **kwargs: Any) -> None:
        """
        Метод, настраивающий модель CNN для обнаружения аномалий с использованием TensorFlow и Keras.

        Алгоритм:
        1. инициализация входного слоя на основе входных данных;
        2. создание сверточных слоев с использованием гиперапараметров: количество фильтров, размер ядра, функция активации, способ заполнения;
        3. после каждого нового слоя применяется регуляризация Dropout;
        4. после Dropout применяется BatchNormalization;
        6. после BatchNormalization применяется уменьшение размера данных с помощьюMaxPooling;
        7. преобразование последнего сверточного слоя в одномерный массив с помощью Flatten;
        8. создание полносвязного слоя с использованием гиперпараметров: количество нейронов, функция активации;
        9. создание выходного слоя с использованием гиперпараметров: количество нейронов, функция активации;
        10. формирование модели с входными и выходными слоями.

        Аргументы:
        input_shape: форма входных данных
        *args, **kwargs: дополнительные аргументы
        """

        # TODO: расширить входные параметры

        self.input_shape = input_shape
        self.input_layer = Input(input_shape)
        self.conv1 = tf.keras.layers.Conv1D(filters=64, kernel_size=11, activation='relu', padding="same")(self.input_layer)
        self.conv1 = Dropout(0.2)(self.conv1)
        self.conv1 = tf.keras.layers.BatchNormalization()(self.conv1)
        self.conv1 = tf.keras.layers.MaxPooling1D(pool_size=2)(self.conv1)

        self.conv2 = tf.keras.layers.Conv1D(filters=64, kernel_size=11, activation='relu', padding="same")(self.conv1)
        self.conv2 = Dropout(0.2)(self.conv2)
        self.conv2 = tf.keras.layers.BatchNormalization()(self.conv2)
        self.conv2 = tf.keras.layers.MaxPooling1D(pool_size=2)(self.conv2)

        self.conv3 = tf.keras.layers.Conv1D(filters=64, kernel_size=11,activation='relu', padding="same")(self.conv2)
        self.conv3 = Dropout(0.2)(self.conv3)
        self.conv3 = tf.keras.layers.BatchNormalization()(self.conv3)
        self.conv3 = tf.keras.layers.MaxPooling1D(pool_size=2)(self.conv3)

        self.flat = Flatten()(self.conv3)

        self.dense1 = tf.keras.layers.Dense(100, activation='relu')(self.flat)
        self.output_layer = tf.keras.layers.Dense(2, activation="softmax")(self.dense1)

        self.model = Model(inputs=self.input_layer, outputs=self.output_layer)

    def __setup_data(self, data: pd.DataFrame, normal_periods=None, failures_periods=None, training=True, *args: Any, **kwargs: Any):
        """
        Метод подготовки данных для обучения модели

        Алгоритм:
        1. если параметр training=True - подготовка данных для обучения: стандартизация данных, создание списка тренировочных данных, преобразование тренировочных данных в последовательности обучающих данных для модели;
        2. если параметр training=False: также стандартизация данных, но не создает обучющие данные.

        Аргументы:
        data (pd.DataFrame): данные
        normal_periods (list): список из словарей с датами участков нормальных периодов
        failures_periods (list): список из словарей с датами участков отказных периодов
        training (bool): флаг обучения
        """

        if training:
            scaled_data = self.__scale_data(data, normal_periods, failures_periods)
            train_list = self._create_train_list(scaled_data, normal_periods, failures_periods)
            index_cur_time_train, X, Y = self._list_to_train_sequenses(train_list, win_size=48)
            X_scaled = self._scale_window(X)
            index_cur_time_train, self.X_scaled, self.Y = self._do_shuffle(index_cur_time_train, X_scaled, Y)
        else:
            # можно засунуть в scale data с training=False
            scaled_data = pd.DataFrame(self.scaler_object.transform(data), index=data.index, columns=data.columns)

            index_cur_time_train, X = self.__to_predict_sequences(scaled_data)
            self.X = self._scale_window(X)


    def __to_predict_sequences(self, data: pd.DataFrame, history_size: int = 48):
        """    
        Метод подготовки данных для прогнозирования

        Алгоритм:
        1. создание списка для хранения последовательных срезов длиной history_size из данных data;
        2. цикл по данным, извлекая срезы длиной history_size из исходных данных и добавляя их в список data_values, также сохраняется индекс текущей временной метки.

        Аргументы:
        data (pd.DataFrame): данные
        history_size (int): размер окна прогнозирования

        Возврат:
        index_cur_time (list): список индексов текущей временной метки
        data_values (np.array): трехмерный массив, список срезов данных размерности (len(data) - history_size, history_size, num_features)
        """

        data_values = []
        index_cur_time = []

        for i in range(len(data)-history_size):
            input = data.iloc[i:i+history_size, :].values
            data_values.append(input)
            index_cur_time.append(data.index[i+history_size])

        return index_cur_time, np.array(data_values)


    def fit(self, data: pd.DataFrame, normal_periods=None, failures_periods=None, BATCH_SIZE=32, validation_split=0.2, EPOCHS=15):
        """
        Метод для обучения данных

        Аргументы:
        data (pd.DataFrame): данные
        normal_periods (list):список из словарей с датами участков нормальных периодов
        failures_periods (list): список из словарей с датами участков отказных периодов
        BATCH_SIZE (int): размер батча
        validation_split (float): доля данных для валидации
        EPOCHS (int): количество эпох

        Алгоритм:
        1. сохранение данных и вызов метода __setup_data для подготовки данных;
        2. вызов метода __setup_model для подготовки модели;
        3. компиляция модели с использованием гиперпараметров: оптимизатор, функция потерь, метрика;
        4. инициализация коллбэков;
        5. обучение модели;
        6. задается порог для обнаружения аномалий = 0.5.
        """

        self.data = data
        self.__setup_data(data=self.data, normal_periods=normal_periods, failures_periods=failures_periods, training=True)

        self.__setup_model(input_shape=self.X_scaled.shape[1:])

        self.model.compile(
            optimizer=tf.keras.optimizers.Nadam(learning_rate=0.001),
            loss='BinaryCrossentropy',
            metrics=['accuracy'])

        callbacks = [DWELL(model=self.model, monitor_acc=False, factor=0.985, verbose=False)]

        self.model.fit(
            self.X_scaled,
            self.Y,
            batch_size=BATCH_SIZE,
            epochs=EPOCHS,
            callbacks=callbacks,
            validation_split=validation_split,
            verbose=0,
            use_multiprocessing=True,
        )

        keras.backend.clear_session()
        self.anomaly_threshold = 0.5
        self.model_object = self.model

        return self

    def predict(self, data: pd.DataFrame):
        """
        Метод для прогнозирования

        Аргументы:
        data (pd.DataFrame): данные

        Алгоритм:
        1. вызов метода __setup_data для подготовки данных;
        2. прогнозирование данных с использованием обученной модели.
        3. создание серии данных интегральной ошибки (вероятность отказа) и статуса аномилй на основе прогнозирований.
        """

        self.data = data
        # оставить, чтобы не забывать
        # self.data = data.iloc[:50] # для теста- работает - получается 2 точки
        # self.data = data.iloc[:48] # для теста -  НЕ работает
        # self.data = data.iloc[:49]  # для теста - работает - получается 1 точка
        self.__setup_data(data=self.data, training=False)

        self.preds = self.model.predict(self.X)
        self.preds = self.preds[:, 0] # - отказ

        self.integral_error = pd.Series(data=self.preds, index=self.data.index[:len(self.preds)]) # вероятность отказа
        self.anomaly_status = pd.Series(
            data=self.integral_error > self.anomaly_threshold, index=self.data.index[:len(self.preds)]
        ).astype(int)
        keras.backend.clear_session()

    def fit_predict(self, data: pd.DataFrame, BATCH_SIZE=10, validation_split=0.2, EPOCHS=20):

        self.fit(data=pd.DataFrame, BATCH_SIZE=BATCH_SIZE, validation_split=validation_split, EPOCHS=EPOCHS)
        self.model.predict(data)
        return self.preds

    def __scale_data(self, data: pd.DataFrame, normal_periods: list, failures_periods: list):
        """
        Метод для масштабирования данных

        Алгоритм:
        1. создание пустого датафрейма df_train, в цикле добавляются нормальные периоды;
        2. в цикле добавляются отказы;
        3. масштабирование данных с помощью StandardScaler;
        4. преобразование масштабированных данных в pd.DataFrame.

        Аргументы:
        data (pd.DataFrame): данные
        normal_periods (list): список из словарей с датами участков нормальных периодов
        failures_periods (list): список из словарей с датами участков отказных периодов

        Возврат:
        df_scaled (pd.DataFrame): масштабированные данные
        """

        df_train = pd.DataFrame(columns=data.columns, index=[])
        for period in normal_periods:
            period_data = data[period['begin']:period['end']]
            df_train = pd.concat([df_train, period_data])
        for failur in failures_periods:
            failur_data = data[failur['begin']:failur['end']]
            df_train = pd.concat([df_train, failur_data])
        self.scaler_object = StandardScaler()
        self.scaler_object.fit(df_train)
        df_scaled = pd.DataFrame(self.scaler_object.transform(data), index=data.index, columns=data.columns) 
        return df_scaled

    def _create_train_list(self, data: pd.DataFrame, normal_periods: list, failures_periods: list):
        """
        Метод для создания списка тренировочных данных.

        Алгоритмы:
        1. Создание пустого списка samplelist для хранения данных обучающей выборки;
        2. Для каждого периода в списке normal_periods:
            2.1. Извлечение данных из исходного DataFrame data с начальной по конечную дату включительно и сохранение в переменной perioddata;
            2.2. Добавление нового столбца 'failure' со значением 0.0 к данным периода;
            2.3. Добавление нового столбца 'normal' со значением 1.0 к данным периода;
            2.4. Добавление perioddata в список samplelist.
        3. Для каждой неисправности в списке failures_periods:
            3.1. Извлечение данных из исходного DataFrame data с начальной по конечную дату включительно и сохранение в переменной perioddata;
            3.2. Добавление нового столбца 'failure' со значением 1.0 к данным периода;
            3.3. Добавление нового столбца 'normal' со значением 0.0 к данным периода.
            3.4. Добавление perioddata в список samplelist.

        Аргументы:
        data (pd.DataFrame): данные
        normal_periods (list): список из словарей с датами участков нормальных периодов
        failures_periods (list): список из словарей с датами участков отказных периодов

        Возврат:
        sample_list (list): список тренировочных данных
        разметка: добавление таргета
        """

        sample_list = []
        for period in normal_periods:
            period_data = data[period['begin']:period['end']]
            period_data['failure'] = 0.0
            period_data['normal'] = 1.0
            sample_list.append(period_data)
        for failur in failures_periods:
            period_data = data[failur['begin']:failur['end']]
            period_data['failure'] = 1.0
            period_data['normal'] = 0.0
            sample_list.append(period_data)
        return sample_list

    def _list_to_train_sequenses(self, sample_list, win_size):
        """    
        Метод для преобразования списка выборок в тренировочные последовательности данных.

        Алгоритм:
        1. создание пустого трехмерного массива X, двумерного массива Y и списка index_cur_time_train. Y имеет два столбца для таргета, а по длине оба как index_cur_time_train (по длине обучающих выборок);
        2. цикл по всем элементам sample_list, если длина выборки меньше win_size, то пропускаем ее;
        3. Для каждой выборки, удовлетворяющей условию, вызывается метод _to_train_sequences для преобразования данных истории входов _df.drop(columns=target) и целевых меток _df[target];
        4. В цикле добавляются полученные данные в массивы X, Y и список index_cur_time_train.

        Аргументы:
        sample_list (list): список тренировочных данных
        win_size (int): размер окна

        Возврат:
        index_cur_time_train (list): список индексов выборок
        X (np.array): тренировочные последовательности данных
        Y (np.array): целевые метки
        """

        target= ['failure', 'normal']
        index_cur_time_train = []
        X = np.array([[[]]*(sample_list[0].shape[1]-2)]*win_size).reshape((0, win_size, (sample_list[0].shape[1]-2)))
        Y = np.array([[],[]]).reshape((0, 2))
        for _df in sample_list:
            if _df.shape[0] < win_size:
                continue
            _index_cur_time_train, _X, _Y = self._to_train_sequences(_df.drop(columns=target), _df[target], history_size = win_size)
            index_cur_time_train += _index_cur_time_train
            X = np.concatenate((X,_X))
            Y = np.concatenate((Y,_Y))
        return index_cur_time_train, X, Y

    def _scale_window(self, X):
        """
        Метод для масштабирования окна.

        Алгоритм:
        1. вычисление среднего значения по осям 1 и 2 массива X (сначала берется среднее по второй оси, потом по второй - результат среднее по всем элементам), в итоге получаются средние значения каждого окна;
        2. повторение по X.shape[2] среднего значения во всех осях и транспонирование;
        3. повторение, но уже по X.shape[1] среднего значения во всех осях и транспонирование;
        4. вычисление масштабированного массива: оно заключается в том, что мы от каждого элемента окна отнимаем среднее значение всех элементов этого окна.

        Аргументы:
        X (np.array): тренировочные последовательности данных

        Возврат:
        X_scaled (np.array): масштабированные тренировочные последовательности данных
        """

        win_mean = np.mean(np.mean(X,axis=1),axis=1)
        win_mean = np.tile(win_mean,(X.shape[2],1)).transpose((1,0))

        win_mean = np.tile(win_mean,(X.shape[1],1,1)).transpose((1,0,2))
        X_scaled = X - win_mean
        return X_scaled

    def _to_train_sequences(self, x, y, history_size):
        """
        Метод для преобразования данных в последовательности для обучения модели.

        Алгоритм:
        1. создание пустых списков index_cur_time, x_values, y_values;
        2. цикл по длине массива x за вычетом history_size;
        3. для каждой итерации цикла берется подмассив x.iloc[i:i+history_size, :] и y.iloc[i+history_size, :];
        4. добавляются полученные данные в списки index_cur_time, x_values, y_values.

        Аргументы:
        x (pd.DataFrame): тренировочные последовательности данных
        y (pd.DataFrame): целевые метки
        history_size (int): размер окна

        Возврат:
        index_cur_time (list): список индексов выборок
        x_values (np.array): тренировочные последовательности данных, на выходе отличаются от входа: входные данные содержат историческую информацию, а выходные содержат целевые значения, соответствующие следующему временному шагу
        y_values (np.array): целевые метки
        """

        x_values = []
        y_values = []
        index_cur_time = []
        
        for i in range(len(x)-history_size):
            input  = x.iloc[i:i+history_size, :].values
            x_values.append(input)
            output = y.iloc[i+history_size, :]
            y_values.append(output)
            index_cur_time.append(x.index[i+history_size])

        return index_cur_time, np.array(x_values),  np.array(y_values)
    
    def _do_shuffle(self, index_cur_time, X_train, y_train):
        """
        Метод для перемешивания тренировочных данных.

        Аргументы:
        index_cur_time (list): список индексов выборок
        X_train (np.array): тренировочные последовательности данных
        y_train (np.array): целевые метки

        Возврат:
        index_cur_time (list): список индексов выборок
        X_train (np.array): перемешанные тренировочные последовательности данных
        y_train (np.array): перемешанные целевые метки
        """

        X_train, y_train, index_cur_time = shuffle(X_train, y_train, index_cur_time, random_state=12345)
        return index_cur_time, X_train, y_train

    @classmethod
    def spas_name(cls):
        return 'CNN'
