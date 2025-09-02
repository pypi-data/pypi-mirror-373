from typing import Any, Tuple

from keras import regularizers
from keras.layers import Dense, Input

from spa_models_lib.src.anomalies_detection.base import MultivariateModels
from spa_models_lib.src.anomalies_detection.Multivariate.autoencoders.autoencoder import \
    AutoEncoder


class Deep_AutoEncoder(AutoEncoder, MultivariateModels):

    def __setup_model(self, input_shape: Tuple, *args: Any, **kwargs: Any) -> None:

        self.input_shape = input_shape
        self.input_layer = Input(shape=(self.input_shape[1]))

        self.encoder_l1 = Dense(
            75,
            activation='elu',
            kernel_initializer='glorot_uniform',
            kernel_regularizer=regularizers.l2(0.0),
        )(self.input_layer)

        self.encoder_l2 = Dense(
            55,
            activation='elu',
            kernel_initializer='glorot_uniform',
            kernel_regularizer=regularizers.l2(0.0),
        )(self.encoder_l1)

        self.emded_layer = Dense(
            30,
            kernel_initializer='glorot_uniform',
        )(self.encoder_l2)

        self.decoder_l1 = Dense(
            30,
            kernel_initializer='glorot_uniform',
        )(self.emded_layer)

        self.decoder_l2 = Dense(
            55,
            kernel_initializer='glorot_uniform',
        )(self.decoder_l1)

        self.decoder_l3 = Dense(
            75,
            kernel_initializer='glorot_uniform',
        )(self.decoder_l2)

        self.output_layer = Dense(
            self.input_shape[1],
            kernel_initializer='glorot_uniform',
        )(self.decoder_l3)

        self.model = Model(inputs=self.input_layer, outputs=self.output_layer)

    @classmethod
    def spas_name(cls):
        return 'Deep_AE'
