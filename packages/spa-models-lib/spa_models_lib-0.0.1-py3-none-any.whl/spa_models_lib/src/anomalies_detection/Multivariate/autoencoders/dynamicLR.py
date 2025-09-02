import copy
import numpy as np
import tensorflow as tf
from tensorflow import keras


class DWELL(keras.callbacks.Callback):
    """
    Класс-определение пользовательского класса для обучения модели.
    """

    # best_weights = []
    def __init__(self, model, monitor_acc, factor, verbose):
        """
        Метод инициализации параметров для работы обратного вызова.

        Алгоритм:
        1. вызлв метода инициализации родительского класса;
        2. инициализация локальных переменных.

        Аргументы:
        model (keras.Model): модель
        monitor_acc (bool): мониторинг точности
        factor (float): коэффициент уменьшения
        verbose (bool): вывод сообщения
        """

        super(DWELL, self).__init__()
        self.model = model
        self.initial_lr = float(tf.keras.backend.get_value(model.optimizer.lr))
        self.lowest_vloss = np.inf
        self.best_weights = []
        self.verbose = verbose
        self.factor = factor
        self.monitor_acc = monitor_acc
        self.highest_acc = 0
        self.epoch_num = 0

    def on_epoch_start(self, epoch, logs=None):
        pass

    def on_epoch_end(self, epoch, logs=None):
        """
        Метод, выполняющий в конце каждой эпохи обучение модели и контролирующий изменение параметров модели.

        Алгоритм:
        1. определение текущей скорости обучения;
        2. определение значения функции потерь на валидационном наборе данных в текущей эпохе и значения метрики точности;
        3. проверка на мониторинге метрики точности;
            3.1 если метрика мониторинга не включена, то на мониторинге валидационный loss: 
                3.1.1 если vloss > lowest_vloss, то загружаются лучшие веса модели и уменьшается скорость обучения на значение factor;
                3.1.2 если vloss < lowest_vloss, то lowest_vloss = vloss, сохраняются лучшие веса и увеличивается число эпох;
            3.2 если метрика мониторинга включена, то модель мониторит точность на тренировочной выборке:
                3.2.1 если acc < highest_acc, то загружаются лучшие веса модели и уменьшается скорость обучения на factor;
                3.2.2 если acc > highest_acc, то highest_acc = acc.
        
        Аргументы:
        epoch (int): число эпох
        logs (dict): словарь с логами
        """

        lr = float(tf.keras.backend.get_value(self.model.optimizer.lr))
        vloss = logs.get('val_loss')
        acc = logs.get('mse')
        if self.monitor_acc == False:
            if vloss > self.lowest_vloss:
                # best_model = self.model #load_model("best_model.h5")
                if self.epoch_num > 0:
                    self.model.set_weights(self.best_weights)
                new_lr = lr * self.factor
                tf.keras.backend.set_value(self.model.optimizer.lr, new_lr)
                if self.verbose:
                    print('\n model weights reset to best weights and reduced lr to ', new_lr, flush=True)
            else:
                self.lowest_vloss = vloss
                self.best_weights = copy.deepcopy(self.model.get_weights())
                self.epoch_num = self.epoch_num + 1
        else:
            if acc < self.highest_acc:
                # load_model("best_model.h5")# monitor training accuracy
                best_model = self.model
                self.model.set_weights(best_model.get_weights())
                new_lr = lr * self.factor
                tf.keras.backend.set_value(self.model.optimizer.lr, new_lr)
                if self.verbose:
                    print('\n model weights reset to best weights and reduced lr to ', new_lr, flush=True)
            else:
                self.highest_acc = acc
