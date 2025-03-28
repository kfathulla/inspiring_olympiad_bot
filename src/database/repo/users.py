from typing import Optional

from sqlalchemy import select, update
from sqlalchemy.dialects.postgresql import insert

from src.database.models import User
from src.database.repo.base import BaseRepo


class UserRepo(BaseRepo):
    async def get_or_create_user(
        self,
        user_id: int,
        full_name: str,
        telegram_id: int,
        username: Optional[str] = None,
    ):
        """
        Creates or updates a new user in the database and returns the user object.
        :param user_id: The user's ID.
        :param full_name: The user's full name.
        :param language: The user's language.
        :param username: The user's username. It's an optional parameter.
        :return: User object, None if there was an error while making a transaction.
        """

        insert_stmt = (
            insert(User)
            .values(
                user_id=user_id,
                username=username,
                full_name=full_name,
                telegram_id=telegram_id
            )
            .on_conflict_do_update(
                index_elements=[User.user_id],
                set_=dict(
                    username=username,
                    full_name=full_name,
                    telegram_id=telegram_id
                ),
            )
            .returning(User)
        )
        result = await self.session.execute(insert_stmt)

        await self.session.commit()
        return result.scalar_one()

    async def get_by_id(self, user_id):
        result = await self.session.execute(select(User).where(User.user_id == user_id))
        return result.scalar_one_or_none()

    async def get_all(self, offset: int = 0, limit: int = 100):
        result = await self.session.execute(select(User).order_by(User.created_at).offset(offset).limit(limit))
        return result.scalars().all()

    async def get_by_chat_id(self, chat_id):
        result = await self.session.execute(select(User).where(User.telegram_id == chat_id))
        return result.scalar_one_or_none()

    async def update_user(self, id, full_name, phone, is_registered):
        stmt = (
            update(User)
            .where(User.user_id == id)
            .values(full_name=full_name, phone=phone, is_registered=is_registered)
        )
        
        await self.session.execute(stmt)
        await self.session.commit()