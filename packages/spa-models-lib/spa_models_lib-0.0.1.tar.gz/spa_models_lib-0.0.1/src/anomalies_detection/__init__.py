from spa_models_lib.src.anomalies_detection.Multivariate.autoencoders.autoencoder import AutoEncoder, Model
from spa_models_lib.src.anomalies_detection.Multivariate.autoencoders.deep_autoencoder import Deep_AutoEncoder
from spa_models_lib.src.anomalies_detection.Multivariate.autoencoders.variational_autoencoder import Variational_AutoEncoder
from spa_models_lib.src.anomalies_detection.Multivariate.clustering.bottom_up import BottomUp_kmeans
from spa_models_lib.src.anomalies_detection.Multivariate.convolution.cnn import CNN
from spa_models_lib.src.anomalies_detection.Multivariate.spc import hotelling_t2
from spa_models_lib.src.anomalies_detection.Univariate.freezing_detector import FreezingDetector
from spa_models_lib.src.anomalies_detection.Univariate.outliers_detector import OutliersDetector
from spa_models_lib.src.anomalies_detection.Univariate.trend_detector import TrendDetector
from spa_models_lib.src.anomalies_detection.Multivariate.autoencoders.lstm_autoencoder import LSTM_AutoEncoder

# from spa_models_lib.src.anomalies_detection.Multivariate.autoencoders.lstm_autoencoder import LSTM_AE
# __autoencoders_models__ = [AutoEncoder]
