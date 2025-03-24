from .iservices import IServices
from src.services.users import IUserService, UserService
from src.brokers.storage_brokers import IRepositories
from src.brokers.storage_brokers.implementations import Repositories


class Services(IServices):
    _user_service: IUserService | None

    def __init__(self):
        self.repositories: IRepositories = Repositories()
        self._user_service: IUserService = UserService(services=self, repositories=self.repositories)

    @property
    def user_service(self) -> IUserService:
        if self._user_service is None:
            self._user_service: IUserService = UserService(services=self, repositories=self.repositories)

        return self._user_service
