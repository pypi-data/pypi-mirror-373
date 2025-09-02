from typing import Any, Tuple

from keras import regularizers
from keras.layers import Dense, Input

from spa_models_lib.src.anomalies_detection.base import MultivariateModels
from spa_models_lib.src.anomalies_detection.Multivariate.autoencoders.autoencoder import \
    AutoEncoder

class Variational_AutoEncoder(AutoEncoder, MultivariateModels):

    def __setup_model(self, input_shape: Tuple, *args: Any, **kwargs: Any) -> None:

        self.input_shape = input_shape
        self.input_layer = Input(shape=(self.input_shape[1]))

        self.encoder_l1 = Dense(
            10,
            activation='elu',
            kernel_initializer='glorot_uniform',
            kernel_regularizer=regularizers.l2(0.0),
        )(self.input_layer)

        self.encoder_l2 = Dense(
            10,
            activation='elu',
            kernel_initializer='glorot_uniform'
        )(self.encoder_l1)

        self.z_mean = Dense(
            2
        )(self.encoder_l2)

        self.z_log_var = Dense(
            2
        )(self.z_mean)

        self.emded_layer = Lambda(
            sampling, 
            output_shape=(2,)
        )([z_mean, z_log_var])

        self.decoder_l1 = Dense(
            5,
            kernel_initializer='glorot_uniform'
        )(self.emded_layer)

        decoder_l2 = Dense(
            10, 
            kernel_initializer='glorot_uniform'
        )(self.decoder_l1)

        self.output_layer = Dense(
            self.input_shape[1],
            kernel_initializer='glorot_uniform',
        )(self.decoder_l3)

        self.model = Model(inputs=self.input_layer, outputs=self.output_layer)

    def __sampling(self, args):
        z_mean, z_log_var = args
        batch = K.shape(z_mean)[0]
        dim = K.int_shape(z_mean)[1]
        epsilon = K.random_normal(shape=(batch, dim))
        return z_mean + K.exp(0.5 * z_log_var) * epsilon

    @classmethod
    def spas_name(cls):
        return 'Variational_AE'
