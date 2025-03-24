from abc import ABCMeta, abstractmethod

from src.models.base import PagedList
from src.models.users import User, UserFilter


class IUserService(metaclass=ABCMeta):
    @abstractmethod
    async def add_user(self, user: User) -> User:
        raise NotImplementedError

    @abstractmethod
    async def add_or_update_user(self, user: User) -> User:
        raise NotImplementedError

    @abstractmethod
    async def get_all_users(self, user_filter: UserFilter) -> PagedList[User]:
        raise NotImplementedError

    @abstractmethod
    async def get_user_by_id(self, user_id: int) -> User | None:
        raise NotImplementedError

    @abstractmethod
    async def get_user_by_telegram_id(self, telegram_id: int) -> User | None:
        raise NotImplementedError

    @abstractmethod
    async def update_user(self, user: User) -> User:
        raise NotImplementedError
