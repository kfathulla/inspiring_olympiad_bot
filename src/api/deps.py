from typing import Annotated
from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt
from jwt.exceptions import InvalidTokenError
from pydantic import BaseModel
import time

from src.config import load_config, Config
from src.database.setup import create_session_pool, create_engine
from src.database.repo.requests import RequestsRepo
from src.database.models.users import User

config = load_config(".env")
engine = create_engine(config.db)


async def get_config() -> Config:
    return config


async def get_session() -> AsyncSession:
    session_pool = create_session_pool(engine)
    async with session_pool() as session:
        yield session


async def get_repo(session: AsyncSession = Depends(get_session)) -> RequestsRepo:
    yield RequestsRepo(session)


ConfigDep = Annotated[Config, Depends(get_config)]
SessionDep = Annotated[AsyncSession, Depends(get_session)]
RepoDep = Annotated[RequestsRepo, Depends(get_repo)]


class UserPayload(BaseModel):
    sub: str  # User ID as string (based on your payload)
    username: str
    is_admin: bool
    exp: int

security_scheme = HTTPBearer(
    auto_error=False,
    scheme_name="InspiringBotApi",
    bearerFormat="JWT",
    description="Enter your JWT token in format: Bearer <token>",
)


async def get_current_user(
    repo: Annotated[RequestsRepo, Depends(get_repo)],
    credentials: HTTPAuthorizationCredentials = Depends(security_scheme),
) -> User:
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing authorization header",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if credentials.scheme != "Bearer":
        raise HTTPException(
            status_code=401,
            detail="Invalid authentication scheme",
            headers={"WWW-Authenticate": "Bearer"},
        )

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(credentials.credentials, config.jwt, algorithms=["HS256"])
        print(payload)
        user_payload = UserPayload(**payload)
        print(user_payload)
        if user_payload.exp < time.time():
                raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token expired"
            )
        if user_payload.sub is None:
            raise credentials_exception
    except InvalidTokenError as er:
        raise credentials_exception

    user = await repo.users.get_by_id(int(user_payload.sub))
    if user is None:
        raise credentials_exception
    return user


CurrentUserDep = Annotated[User, Depends(get_current_user)]
