import asyncio
from datetime import datetime

from src.brokers.storage_brokers import IUserStorageBroker
from src.brokers.storage_brokers.implementations import UserStorageBroker
from src.models.users import User, UserFilter
from src.services.services_uow import IServices, Services


async def test_insert():
    user = User(username="firdavs", first_name="Firdavs", last_name=None, phone_number="998974317151", telegram_id=0,
                created_datetime=datetime.now())

    user_storage_broker: IUserStorageBroker = UserStorageBroker()
    inserted_user = await user_storage_broker.insert_user(user)
    print(inserted_user.id)


async def test_get_all():
    services: IServices = Services()
    users = await services.user_service.get_all_users(UserFilter(updated_datetime_from=None,
                                                                 updated_datetime_to=None))
    print(users.__dict__)


async def test_get():
    services: IServices = Services()
    user = await services.user_service.get_user_by_telegram_id(telegram_id=-1)
    print(user.__dict__ if user else "null")


async def test_update():
    services: IServices = Services()
    user = await services.user_service.get_user_by_telegram_id(telegram_id=-1)
    user.telegram_id = -10
    updated_user = await services.user_service.update_user(user=user)
    print(updated_user.__dict__ if updated_user else "null")


loop = asyncio.get_event_loop()
loop.run_until_complete(test_update())
