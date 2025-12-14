import hashlib
import hmac
import json
from typing import Annotated
from urllib.parse import unquote

from fastapi import Depends, Header, HTTPException
from sqlalchemy.orm import Session

from config import settings
from db import SessionLocal
from db.crud import get_or_create_user
from db.models import User


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


SessionDep = Annotated[Session, Depends(get_db)]


def check_hash(data_check_string: str, hash: str) -> bool:
    for token in settings.TRUSTED_API_TOKENS:
        secret_key = hmac.new(b"WebAppData", token.encode(), hashlib.sha256).digest()
        res = hmac.new(
            secret_key, data_check_string.encode(), hashlib.sha256
        ).hexdigest()
        if res == hash:
            return True
    raise HTTPException(status_code=401, detail="Invalid authorization")


async def get_user(
    db: SessionDep, authorization: str | None = Header(default=None)
) -> User | None:
    # Без авторизации — сразу None, чтобы не падать
    if not authorization:
        return None

    parts = authorization.split(" ", 1)
    token = parts[1] if len(parts) == 2 else parts[0]
    token = unquote(token)

    if not token:
        return None

    data = token.split("&")

    data_check_string = "\n".join(
        sorted(filter(lambda kv: not kv.startswith("hash"), data))
    )
    init_data = dict(x.split("=") for x in data if "=" in x and x)

    if "hash" not in init_data or "user" not in init_data:
        raise HTTPException(status_code=401, detail="Invalid authorization")

    check_hash(data_check_string, init_data["hash"])

    json_data = json.loads(init_data["user"])
    return get_or_create_user(
        db, json_data["id"], json_data.get("first_name"), json_data.get("username")
    )


UserDep = Annotated[User, Depends(get_user)]
