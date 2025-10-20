from fastapi import APIRouter, Form, HTTPException
from typing import Annotated
from fastapi.responses import JSONResponse
import time, hashlib, hmac, urllib.parse, json
import jwt

from src.api.deps import RepoDep, ConfigDep

auth_router = APIRouter(
    prefix="/api/auth",
    tags=["auth"])


def verify_init_data(init_data: str, cfg: ConfigDep):
    parsed = urllib.parse.parse_qs(init_data, keep_blank_values=True)
    print(parsed)
    hash_from_telegram = parsed.pop("hash")[0]
    data_check_string = '\n'.join(f"{k}={v[0]}" for k,v in sorted(parsed.items()))
    secret_key = hmac.new(
        key=b"WebAppData",
        msg=cfg.tg_bot.token.encode(),
        digestmod=hashlib.sha256
    ).digest()
    computed_hash = hmac.new(
        key=secret_key,
        msg=data_check_string.encode(),
        digestmod=hashlib.sha256
    ).hexdigest()

    if computed_hash != hash_from_telegram:
        raise HTTPException(status_code=403, detail="Invalid init data")

    return json.loads(parsed.get("user")[0])

@auth_router.post("/login-with-tg-sign")
async def login_with_tg_sign(
    init_data: Annotated[str, Form()],
    repo: RepoDep,
    cfg: ConfigDep
):
    user = verify_init_data(init_data, cfg)
    
    payload = {
        "sub": f"{user["id"]}",
        "username": user["username"],
        "is_admin": int(int(user["id"])) in cfg.tg_bot.admin_ids,
        "exp": int(time.time()) + 60 * 60 * 24
    }

    token = jwt.encode(payload, cfg.jwt, algorithm="HS256")
    print(token)
    return { "token": token }