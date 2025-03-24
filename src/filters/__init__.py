from src.loader import dp
from .admins_filter import AdminFilter
from .group_filter import GroupFilter
from .private_chat_filter import PrivateFilter

if __name__ == "filters":
    dp.filters_factory.bind(AdminFilter)
    dp.filters_factory.bind(GroupFilter)
    dp.filters_factory.bind(PrivateFilter)
    pass
