from src.brokers.storage_brokers import IRepositories, IUserStorageBroker
from src.brokers.storage_brokers.implementations import UserStorageBroker


class Repositories(IRepositories):
    def __init__(self):
        self._user_repository = None

    @property
    def user_repository(self) -> IUserStorageBroker:
        if self._user_repository is None:
            self._user_repository = UserStorageBroker()

        return self._user_repository
