from abc import ABC, abstractmethod


class OilModels(ABC):
    @abstractmethod
    async def fit(self):
        pass

    @abstractmethod
    async def predict(self):
        pass

    @abstractmethod
    async def fit_predict(self):
        pass
