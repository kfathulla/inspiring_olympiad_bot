from datetime import datetime

from src.models.base import PagedList
from src.models.users import User, UserFilter
from src.services.base import BaseService
from .iuser_service import IUserService


class UserService(IUserService, BaseService):
    def __init__(self, services, repositories):
        BaseService.__init__(self, services=services, repositories=repositories)

    async def add_user(self, user: User) -> User:
        try:
            return await self.repositories.user_repository.insert_user(user)
        except Exception as ex:
            raise ex

    async def add_or_update_user(self, user: User) -> User:
        try:
            storage_user = await self.get_user_by_telegram_id(user.telegram_id)
            date_time = datetime.now()
            user.updated_datetime = date_time
            if storage_user is None:
                user.created_datetime = date_time
                return await self.repositories.user_repository.insert_user(user)
            else:
                user.created_datetime = storage_user.created_datetime
                user.id = storage_user.id
                user.phone_number = user.phone_number or storage_user.phone_number
                return await self.repositories.user_repository.update_user(user)
        except Exception as ex:
            raise ex

    async def get_all_users(self, user_filter: UserFilter) -> PagedList[User]:
        try:
            return await self.repositories.user_repository.select_all_users(user_filter=user_filter)
        except Exception as ex:
            raise ex

    async def get_user_by_id(self, user_id: int) -> User | None:
        try:
            return await self.repositories.user_repository.select_user(id=user_id)
        except Exception as ex:
            raise ex

    async def get_user_by_telegram_id(self, telegram_id: int) -> User | None:
        try:
            return await self.repositories.user_repository.select_user(telegram_id=telegram_id)
        except Exception as ex:
            raise ex

    async def update_user(self, user: User) -> User | None:
        try:
            return await self.repositories.user_repository.update_user(user=user)
        except Exception as ex:
            raise ex
