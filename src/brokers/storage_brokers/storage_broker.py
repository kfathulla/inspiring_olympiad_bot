from abc import ABCMeta, abstractmethod


class IStorageBroker(metaclass=ABCMeta):
    @abstractmethod
    async def connection(self):
        raise NotImplementedError
