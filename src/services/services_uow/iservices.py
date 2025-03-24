from abc import ABCMeta, abstractmethod

from src.services.users import IUserService


class IServices(metaclass=ABCMeta):
    @property
    @abstractmethod
    def user_service(self) -> IUserService:
        raise NotImplemented

