import asyncpg
from asyncpg import Connection

from src.brokers.storage_brokers import IStorageBroker
from src.config import config


class StorageBroker(IStorageBroker):
    async def connection(self) -> Connection:
        connection = await asyncpg.connect(
            user=config.DB_USER,
            password=config.DB_PASS,
            host=config.DB_HOST,
            port=config.DB_PORT,
            database=config.DB_NAME,
        )

        return connection

    async def execute(
            self,
            connection,
            command,
            *args,
            fetch: bool = False,
            fetch_val: bool = False,
            fetch_row: bool = False,
            execute: bool = False,
    ):
        async with connection.transaction():
            if fetch:
                result = await connection.fetch(command, *args)
            elif fetch_val:
                result = await connection.fetchval(command, *args)
            elif fetch_row:
                result = await connection.fetchrow(command, *args)
            elif execute:
                result = await connection.execute(command, *args)
        return result

    @staticmethod
    def format_args(sql, parameters: dict):
        sql += " AND ".join(
            [f"{item} = ${num}" for num, item in enumerate(parameters.keys(), start=1)]
        )
        return sql, tuple(parameters.values())
