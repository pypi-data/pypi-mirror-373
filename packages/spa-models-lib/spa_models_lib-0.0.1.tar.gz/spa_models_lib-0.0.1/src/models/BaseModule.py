from abc import ABC, abstractmethod
import numpy as np

class SPA_models(ABC):

    @abstractmethod
    async def train(self):
        pass

    @abstractmethod
    async def contribs(self):
        pass

    @abstractmethod
    async def data_preproc(self):
        pass

    @abstractmethod
    async def build_new(self):
        pass

    @abstractmethod
    async def build_exist(self):
        pass
    
    @abstractmethod
    async def calc(self):
        pass


