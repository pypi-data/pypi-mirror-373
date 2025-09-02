from abc import ABC, abstractmethod


class MultivariateModels(ABC):
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


class UnivariateModels(ABC):
    @abstractmethod
    async def fit(self):
        pass

    @abstractmethod
    async def predict(self):
        pass

    @abstractmethod
    async def fit_predict(self):
        pass
