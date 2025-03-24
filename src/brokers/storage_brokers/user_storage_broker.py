from abc import ABCMeta, abstractmethod

from src.models.base import PagedList
from src.models.users import User, UserFilter


class IUserStorageBroker(metaclass=ABCMeta):
    @abstractmethod
    async def insert_user(self, user: User) -> User:
        raise NotImplementedError

    @abstractmethod
    async def select_all_users(self, user_filter: UserFilter) -> PagedList[User]:
        raise NotImplementedError

    @abstractmethod
    async def select_user(self, **kwargs) -> User | None:
        raise NotImplementedError

    @abstractmethod
    async def count_users(self, user_filter: UserFilter) -> int:
        raise NotImplementedError

    @abstractmethod
    async def update_user(self, user: User) -> User:
        raise NotImplementedError
