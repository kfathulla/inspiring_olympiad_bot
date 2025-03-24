from datetime import datetime

from src.brokers.storage_brokers import IUserStorageBroker
from src.brokers.storage_brokers.implementations import StorageBroker
from src.models.base import PagedList
from src.models.users import User, UserFilter


class UserStorageBroker(IUserStorageBroker, StorageBroker):
    async def insert_user(self, user: User) -> User:
        sql = (
            "INSERT INTO users (username, first_name, last_name, phone_number, telegram_id, created_datetime, updated_datetime)"
            " VALUES($1, $2, $3, $4, $5, $6, $7) returning *")

        connection = await self.connection()
        record = await self.execute(connection, sql, user.username, user.first_name, user.last_name,
                                    user.phone_number, user.telegram_id,
                                    user.created_datetime, user.updated_datetime,
                                    fetch_row=True)
        user.id = record["id"]
        await connection.close()

        return user

    async def select_all_users(self, user_filter: UserFilter) -> PagedList[User]:
        sql_filter = (
            " FROM users WHERE (updated_datetime >= $1) "
            " AND (updated_datetime <= $2) ")
        sql_count = "SELECT COUNT(id) " + sql_filter
        sql_select = (
                "SELECT id, username, first_name, last_name, phone_number, telegram_id, created_datetime, updated_datetime, is_deleted "
                + sql_filter + " LIMIT $3 OFFSET $4 ")

        user_filter.updated_datetime_from = user_filter.updated_datetime_from or datetime.min
        user_filter.updated_datetime_to = user_filter.updated_datetime_to or datetime.now()
        connection = await self.connection()
        count = await self.execute(connection, sql_count,
                                   user_filter.updated_datetime_from,
                                   user_filter.updated_datetime_to,
                                   fetch_val=True)
        records = await self.execute(connection, sql_select,
                                     user_filter.updated_datetime_from,
                                     user_filter.updated_datetime_to,
                                     user_filter.page_size, user_filter.skip,
                                     fetch=True)

        user_list = []
        for record in records:
            user = User()
            user.id = record["id"]
            user.username = record["username"]
            user.first_name = record["first_name"]
            user.last_name = record["last_name"]
            user.phone_number = record["phone_number"]
            user.telegram_id = record["telegram_id"]
            user.created_datetime = record["created_datetime"]
            user.updated_datetime = record["updated_datetime"]
            user.is_deleted = record["is_deleted"]
            user_list.append(user)

        await connection.close()

        return PagedList(items=user_list, count=count,
                         page_number=user_filter.page_number,
                         page_size=user_filter.page_size)

    async def select_user(self, **kwargs) -> User | None:
        sql = "SELECT * FROM users WHERE "
        sql, parameters = self.format_args(sql, parameters=kwargs)
        connection = await self.connection()
        record = await self.execute(connection, sql, *parameters, fetch_row=True)
        user: User | None = None
        if record is not None:
            user = User()
            user.id = record["id"]
            user.username = record["username"]
            user.first_name = record["first_name"]
            user.last_name = record["last_name"]
            user.phone_number = record["phone_number"]
            user.telegram_id = record["telegram_id"]
            user.created_datetime = record["created_datetime"]
            user.updated_datetime = record["updated_datetime"]
            user.is_deleted = record["is_deleted"]
        await connection.close()

        return user

    async def count_users(self, user_filter: UserFilter) -> int:
        sql_filter = (
            " FROM users WHERE ($3 IS NULL OR updated_datetime >= $3) "
            " AND ($4 IS NULL OR updated_datetime <= $4)")
        sql_count = "SELECT COUNT(id) " + sql_filter
        connection = await self.connection()
        count = await self.execute(connection, sql_count, fetch_val=True)
        await connection.close()

        return count

    async def update_user(self, user: User) -> User:
        connection = await self.connection()
        sql = (
            "UPDATE users SET username=$1 "
            ", first_name=$2 "
            ", last_name=$3"
            ", phone_number=$4"
            ", updated_datetime=$5"
            ", is_deleted=$6 "
            " WHERE telegram_id=$7")
        await self.execute(connection, sql, user.username, user.first_name, user.last_name,
                           user.phone_number, user.updated_datetime, user.is_deleted,
                           user.telegram_id, execute=True)

        return user
