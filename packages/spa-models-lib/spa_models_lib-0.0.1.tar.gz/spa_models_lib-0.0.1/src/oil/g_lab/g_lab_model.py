import base64
import io

import pandas as pd
from spa_models_lib.src.oil.base import OilModels
from spa_models_lib.src.oil.g_lab import interpretation_lib
from spa_models_lib.src.oil.g_lab.pi_data.create_data import CGlobClass


class GLab(OilModels):

    def fit(self):
        pass

    def predict(self, input_dict,limits_dict,binary_file):

        bytes_io = io.BytesIO(base64.b64decode(binary_file))
        alg_df = pd.read_pickle(bytes_io)

        # класс для хранения данных
        globClass = CGlobClass()

        # запуск интерпретации
        input_data = interpretation_lib.InputData(input_dict)
        int_result = interpretation_lib.InterpretationResult(
            globClass, input_data, alg_df=alg_df, limit_path=limits_dict
        )
        return int_result


    def fit_predict(self):
        pass

    @classmethod
    def spas_name(cls):
        return 'G_lab'
