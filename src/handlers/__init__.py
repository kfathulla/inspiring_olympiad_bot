from .users import user_routers_list
from .groups import group_routers_list

router_list = user_routers_list
router_list += group_routers_list

__all__ = [
    "router_list"
]