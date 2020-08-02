from functools import lru_cache

from App import setting


def msg(code=200, msg='success', data=None):
    if data is None:
        data = []
    return {'code': code, 'msg': msg, 'data': data}


@lru_cache()
def get_setting():
    type = setting.APP_ENV
    return setting.envs.get(type)()
