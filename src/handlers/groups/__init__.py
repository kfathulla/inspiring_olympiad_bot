from .cleaner import cleaner_router
from .moderator import moderator_router
from .reply_message import reply_message_router


group_routers_list = [
    reply_message_router,
    cleaner_router,
    moderator_router
]

__all__ = [
    "group_routers_list",
]
