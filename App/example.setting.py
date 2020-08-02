import os

from pydantic import BaseSettings


class Setting(BaseSettings):
    DEBUG: bool = False
    # cloudflare partner 邮箱
    HOST_MAIL: str = 'mail@qq.com'
    # cloudflare partner 秘钥
    HOST_KEY: str = 'auth_token'
    SECRET_KEY = os.urandom(24)
    ALGORITHM = "HS256"
    # access_token 过期时间
    ACCESS_TOKEN_EXPIRE_MINUTES = 86400
    # 可缓存大小
    CACHE_MAXSIZE = 512
    # 缓存失效时间
    CACHE_TTL = 120


class developConfig(Setting):
    DEBUG: bool = True


class productConfig(Setting):
    DEBUG: bool = False


envs = {
    'develop': developConfig,
    'product': productConfig,
}

APP_ENV = 'product'
