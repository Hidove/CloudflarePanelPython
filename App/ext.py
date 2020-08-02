import functools
import time
from datetime import timedelta, datetime
from functools import lru_cache
from typing import Optional

from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from passlib.context import CryptContext
from starlette import status

from App.utils.common import get_setting

from cacheout import Cache

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
setting = get_setting()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, setting.SECRET_KEY, algorithm=setting.ALGORITHM)
    return encoded_jwt


def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, setting.SECRET_KEY, algorithms=[setting.ALGORITHM])

    except JWTError:
        raise credentials_exception
    return payload


@lru_cache()
def get_cache_driver():
    return Cache(maxsize=setting.CACHE_MAXSIZE, ttl=setting.CACHE_TTL, timer=time.time, default=None)


# 内存缓存 根据函数__name__+位置参数+顺序参数生产 hash key值
def memorize_cache():
    cache = get_cache_driver()

    def decorator(func):
        @functools.wraps(func)
        def wrap(*args, **kw):
            cache_key = func.__name__ + '#' + str(args.__str__().__hash__()) + '#' + str(kw.__str__().__hash__())
            data = cache.get(cache_key)
            if data:
                return data
            data = func(*args, **kw)
            cache.set(cache_key, data)
            return data

        return wrap

    return decorator
