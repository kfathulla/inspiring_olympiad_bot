from .start import admin_start_router
from .tests import admin_tests_router
from .ad import admin_ad_router

admin_routers_list = [
    admin_start_router,
    admin_tests_router,
    admin_ad_router
]

__all__ = [
    "admin_routers_list",
]
