from .ibase_service import IBaseService


class BaseService(IBaseService):
    repositories: any
    services: any

    def __init__(self, services, repositories):
        self.services = services
        self.repositories = repositories
