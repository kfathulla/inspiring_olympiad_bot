from src.loader import dp
from .check_subscription import BigBrother
from .throttling import ThrottlingMiddleware

if __name__ == "middlewares":
    # dp.middleware.setup(BigBrother())
    dp.middleware.setup(ThrottlingMiddleware())
