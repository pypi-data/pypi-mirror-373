from typing import Any, Dict, List, Tuple, Union
import keras
import numpy as np
import pandas as pd
import tensorflow as tf
from keras import regularizers
from keras.layers import Dense, Input
from sklearn.preprocessing import MinMaxScaler
from tensorflow.keras.models import Model as ModelKeras
from tensorflow.python.keras.saving import saving_utils
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


class AutoEncoder(MultivariateModels):
    """
    Класс для обучения и предсказания аномальных значений с помощью автоэнкодера.
    """

    MODEL_TYPE = 'MULTIVARIATE_ANOMALY'

    def get_model(self,
        model_config: Dict = None,
        model_weights: List = None,
        threshold: Union[float, int] = None,
        model_object: Any = None,
        weighted_errors_mode: str = 'off',
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
        scaler_object=None: объект масштабирования данных
        *args: любые другие аргументы
        **kwargs: любые другие ключевые аргументы
        """

        self.scaler_object = scaler_object
        self.anomaly_threshold = threshold
        self.weighted_errors_mode = weighted_errors_mode
        self.error_weights = pd.Series(error_weights)
    

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
        Метод, инициализирующий модель нейронной сети для автоэнкодера.

        Алгоритм:
        1. задается форма входных данных, в данном случае это кортеж, первый элемент которого обозначает количество признаков во входных данных;
        2. определяется входной слой модели, где форма слоя соответствует количеству признаков;
        3. формирование энкодера, скрытого слоя и декодера с произвольными параметрами: количество нейронов на слое, регуляризатор, инициализация весов, функция активации;
        4. формирование выходного слоя автоэнкодера
        ВАЖНО! У автоэнкодера количество нейронов на входном слое равно количеству нейронов на выходном слое
        (количество признаков входных данных равно количеству признаков выходных данных);
        5. создается модель с указанием входного и выходного слоев

        Аргументы:
        input_shape: Tuple: форма входных данных (кортеж)
        *args: Any: любые другие параметры
        **kwargs: Any: любые другие ключевые параметры
        """

        # TODO: расширить входные параметры

        self.input_shape = input_shape
        self.input_layer = Input(shape=(self.input_shape[1]))

        self.encoder_l1 = Dense(
            10,
            activation='elu',
            kernel_initializer='glorot_uniform',
            # kernel_initializer='ones', kernel_initializer='zeros' (здесь и далее)
            kernel_regularizer=regularizers.l2(0.0),
        )(self.input_layer)

        self.emded_layer = Dense(
            2,
            kernel_initializer='glorot_uniform',
        )(self.encoder_l1)

        self.decoder_l1 = Dense(
            10,
            kernel_initializer='glorot_uniform',
        )(self.emded_layer)

        self.output_layer = Dense(
            self.input_shape[1],
            kernel_initializer='glorot_uniform',
        )(self.decoder_l1)

        self.model = Model(inputs=self.input_layer, outputs=self.output_layer)

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

    def fit(self, 
            data: pd.DataFrame, 
            BATCH_SIZE=10, 
            validation_split=0.2, 
            EPOCHS=20, 
            weighted_errors_mode: str = 'off',
            error_weights: list = None
            ):

        """
        Метод обучения модели на на нормальных данных (данные, которые не содержат аномалии).

        Алгоритм:
        1. обработка данных с помощью метода __setup_data;
        2. инициализация модели с помощью метода __setup_model;
        3. компиляция модели с помощью метода compile и выбранными оптимизатором и функцией потерь;
        4. обучение модели на масштабированных данных;
        6. прогноз модели на обучающих данных;
        7. вычисление разницы между прогнозом и масштабированными данными;
        8. определение порога аномалий с помощью метода __get_threshold;
        9. определение важности признаков с помощью метода __get_contribs;
        10. вычисление интегральной ошибки, статуса аномалий;
        11. определение весов и конфига.

        Аргументы:
        data: pd.DataFrame: исходные данные (обучение происходит на нормальных данных)
        BATCH_SIZE: int: размер батча
        validation_split: float: доля данных для проверки
        EPOCHS: int: количество эпох
        """

        self.data = data
        processed_data = self.__setup_data(data=self.data, training=True)

        self.weighted_errors_mode = weighted_errors_mode

        self.__setup_model(input_shape=processed_data.shape)

        self.model.compile(optimizer=tf.keras.optimizers.Adam(learning_rate=0.001), loss='mae')
        callbacks = [DWELL(model=self.model, monitor_acc=False, factor=0.95, verbose=False)]

        self.model.fit(
            processed_data,
            processed_data,
            batch_size=BATCH_SIZE,
            epochs=EPOCHS,
            callbacks=callbacks,
            validation_split=validation_split,
            verbose=0,
            use_multiprocessing=True,
        )

        self.preds = pd.DataFrame(data=self.model.predict(processed_data), index=self.data.index)
        keras.backend.clear_session()
        self.resids = np.abs(self.preds - processed_data)

        self.__calc_weights(error_weights)
        self.__get_contribs()

        self.integral_error = self.__calc_integral_error()

        self.__get_threshold()

        self.anomaly_status = pd.Series(
            data=self.integral_error > self.anomaly_threshold, index=self.data.index
        ).astype(int)

        self.model_weights = self.model.get_weights()
        self.model_config = self.model.get_config()

        self.model_object = self.model

        return self
    
    def __calc_weights(self, error_weights):
        if self.weighted_errors_mode == 'manual':
            self.error_weights = pd.Series(error_weights)
        else:
            self.error_weights = 1 / self.resids.std()
            self.error_weights = (self.error_weights - self.error_weights.min()) * 0.5 + self.error_weights.min()
        self.error_weights = self.error_weights / self.error_weights.sum()

    def __calc_integral_error(self, weights=None):
        if self.weighted_errors_mode != 'off':
            weights = self.error_weights
        return pd.Series(data=np.average(a=self.resids, axis=1, weights=weights), index=self.data.index)

    def __get_threshold(self):

        """
        Метод для определения порогового значения аномалий.

        np.mean(self.resids, axis=1) - среднее значение остатков модели по всем наблюдениями.
        Остатки есть разница фактических значений и прогнозов

        np.quantile(a=np.mean(self.resids, axis=1), q=0.999) - вычисление квантиля уровня 0.999 (99.9%).
        Это означает, что 99.9% значений остатков будут меньше или равны пороговому значению
        """

        self.anomaly_threshold = np.quantile(a=self.integral_error, q=0.999)  # *self.error_weights

    # def __get_param_weights(self):
    # расчет весов
    # self.error_weights = 1 / (np.mean(train_error, axis=0) / np.mean(train_error, axis=0).sum())
    # self.error_weights = self.error_weights / sum(self.error_weights)

    def predict(self, data: pd.DataFrame):

        """
        Метод для расчета данных.

        Алгоритм:
        1. вызывается метод __setup_data для обработки данных, переданных в качестве входных данных, training=False означает, что данные используются для расчета, а не обучения;
        2. производится расчет с использованием обученной модели на обработанных данных с последующим сохранением в preds;
        3. вычисляются остатки, интегральная ошибка, статус аномалий;
        4. вызов метода для получения информации о вкладах признаков.
        
        Аргументы:
        data: pd.DataFrame: данные для прогнозирования
        """
        self.data = data
        processed_data = self.__setup_data(data=self.data, training=False)
        self.preds = pd.DataFrame(
            data=self.model.predict(processed_data), index=self.data.index
        )  # * self.error_weights
        self.resids = np.abs(self.preds - processed_data)
        self.integral_error = self.__calc_integral_error()
        self.anomaly_status = pd.Series(
            data=self.integral_error > self.anomaly_threshold, index=self.data.index
        ).astype(int)
        self.__get_contribs()
        keras.backend.clear_session()

    def fit_predict(self, data: pd.DataFrame, BATCH_SIZE=10, validation_split=0.2, EPOCHS=20):
        
        """
        Метод, объединяющий методы fit и predict.

        Алгоритм:
        1. вызов метода fit для обучения модели на переданных данных;
        2. после обучения вызывается метод predict для расчета на тех же самых данных, что были поданы на обучение

        Аргументы:
        data: pd.DataFrame: данные для обучения и прогнозирования
        BATCH_SIZE: int: размер батча
        validation_split: float: доля данных для проверки
        EPOCHS: int: количество эпох
        
        Возврат:
        preds: pd.DataFrame: прогнозированные значения
        """

        self.fit(data=pd.DataFrame, BATCH_SIZE=BATCH_SIZE, validation_split=validation_split, EPOCHS=EPOCHS)
        self.model.predict(data)
        return self.preds

    def __get_contribs(self, weights=1):

        """
        Метод для вычисления вкладов признаков.

        Алгоритм:
        Определяется вклад параметра, как отношениее частной ошибки параметра к общей ошибки автоэнкодера в данной временной метке
        """
        if self.weighted_errors_mode != 'off':
            weights = self.error_weights
        resids = self.resids * weights
        a_values = resids.values
        b_values = np.sum(resids.values, axis=1).reshape(-1, 1)
        error_contrib = np.divide(a_values, b_values,where=b_values!=0,out=np.zeros_like(a_values))
        self.anomaly_contribs = pd.DataFrame(data=error_contrib, index=self.data.index, columns=self.data.columns)

    @classmethod
    def spas_name(cls):
        return 'Vanilla_AE'
