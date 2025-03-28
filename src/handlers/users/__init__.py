# ADMIN

# MANAGER


# USER
from .start import start_router
from .help import help_router
from .echo import echo_router
from .profile import profile_router
from .register import register_router
from .tests import tests_router

user_routers_list = [
    start_router,
    help_router,
    tests_router,
    profile_router,
    register_router,
    echo_router
]

__all__ = [
    "user_routers_list",
]
