from abc import ABCMeta, abstractmethod

from src.brokers.storage_brokers import IUserStorageBroker


class IRepositories(metaclass=ABCMeta):
    @property
    @abstractmethod
    def user_repository(self) -> IUserStorageBroker:
        raise NotImplemented
