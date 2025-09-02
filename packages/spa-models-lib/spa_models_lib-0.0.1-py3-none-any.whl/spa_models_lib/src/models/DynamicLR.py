from tensorflow import keras
import tensorflow as tf
from tensorflow.keras.callbacks import EarlyStopping, ModelCheckpoint, LearningRateScheduler
from keras.models import load_model
import numpy as np
import copy


class DWELL(keras.callbacks.Callback):
    # best_weights = []
    def __init__(self, model, monitor_acc,  factor, verbose):
        super(DWELL, self).__init__()
        self.model=model
        self.initial_lr=float(tf.keras.backend.get_value(model.optimizer.lr)) # get the initiallearning rate and save it  
        self.lowest_vloss=np.inf # set lowest validation loss to infinity initially
        self.best_weights=[] # set best weights to model's initial weights 
        self.verbose=verbose
        self.factor=factor
        self.monitor_acc= monitor_acc
        self.highest_acc=0
        self.epoch_num = 0


    def on_epoch_start(self, epoch, logs=None):
        pass

    def on_epoch_end(self, epoch, logs=None):  # method runs on the end of each epoch
        lr=float(tf.keras.backend.get_value(self.model.optimizer.lr)) # get the current learning rate        
        vloss=logs.get('val_loss')  # get the validation loss for this epoch 
        acc=logs.get('mse')
        if self.monitor_acc==False:# monitor validation loss
            if vloss>self.lowest_vloss:
                # best_model = self.model #load_model("best_model.h5")
                if self.epoch_num>0:
                    self.model.set_weights(self.best_weights)
                new_lr=lr * self.factor
                tf.keras.backend.set_value(self.model.optimizer.lr, new_lr)
                if self.verbose:
                    print( '\n model weights reset to best weights and reduced lr to ', new_lr, flush=True)
            else:
                self.lowest_vloss=vloss
                self.best_weights = copy.deepcopy(self.model.get_weights())
                self.epoch_num = self.epoch_num + 1
        else:
            if acc< self.highest_acc:
                best_model = self.model  #load_model("best_model.h5")# monitor training accuracy
                self.model.set_weights(best_model.get_weights())
                new_lr=lr * self.factor
                tf.keras.backend.set_value(self.model.optimizer.lr, new_lr)
                if self.verbose:
                    print( '\n model weights reset to best weights and reduced lr to ', new_lr, flush=True)
            else:
                self.highest_acc=acc