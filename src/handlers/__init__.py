from .users import user_routers_list
from .users.admins import admin_routers_list

router_list = admin_routers_list
router_list += user_routers_list

__all__ = [
    "router_list"
]