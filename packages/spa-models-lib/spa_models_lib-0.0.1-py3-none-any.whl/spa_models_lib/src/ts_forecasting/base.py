from abc import ABC, abstractmethod
from dataclasses import dataclass, field, fields
from typing import Any, Dict, List, Optional, Tuple, Union

import numpy as np
import pandas as pd


@dataclass
class ForecastingOutputs:
    date_prediction_unix: float = None
    date_prediction: str = None
    predictions: pd.Series = None
    forecasts: pd.Series = None

    def __post_init__(self):
        ...

    def __repr__(self):
        return self.__class__.__name__

    # def __getattribute__(self, attr):
    #     try:
    #         return self.__getattribute__(attr)
    #     except:
    #         return None

    @classmethod
    def from_dict(cls, dict_):
        class_fields = {f.name for f in fields(cls)}
        return ForecastingOutputs(**{k: v for k, v in dict_.items() if k in class_fields})


class TSForecasting(ABC):
    def _type(self):
        return self.__class__.__name__

    @abstractmethod
    async def fit(self):
        pass

    @abstractmethod
    async def predict(self):
        pass

    @abstractmethod
    async def fit_predict(self):
        pass

    @abstractmethod
    async def fit_predict(self):
        pass
