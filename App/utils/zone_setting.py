import CloudFlare

from App import HidoveException
from App.ext import memorize_cache as cache
from App.utils.common import msg


# 获取所有设置
@cache()
def get_all_zone_settings(cf, zone_id):
    try:
        settings_get = cf.zones.settings.get(zone_id)
    except CloudFlare.exceptions.CloudFlareAPIError as e:
        raise HidoveException(status_code=400, message=e)

    return msg(200, 'success', settings_get)


# 获取 目标 设置
@cache()
def get_zone_setting(cf, zone_id, type='always_online'):
    try:
        settings_get = getattr(cf.zones.settings, type).get(zone_id)
    except CloudFlare.exceptions.CloudFlareAPIError as e:
        raise HidoveException(status_code=400, message=e)

    return msg(200, 'success', settings_get)


# 批量更新设置
def do_zone_settings_update(cf, zone_id, data):
    try:
        settings_get = cf.zones.settings.patch(zone_id, data={'items': data})
    except CloudFlare.exceptions.CloudFlareAPIError as e:
        raise HidoveException(status_code=400, message=e)

    return msg(200, 'success', settings_get)


# 更新 目标 设置
def do_zone_setting_update(cf, zone_id, type='always_online', data=None):
    if data is None:
        data = {}
    try:
        settings_get = getattr(cf.zones.settings, type).patch(zone_id, data={'value': data})
    except CloudFlare.exceptions.CloudFlareAPIError as e:
        raise HidoveException(status_code=400, message=e)
    return msg(200, 'success', settings_get)


# 获取页面规则
@cache()
def get_zone_pagerules(cf, zone_id):
    try:
        pagerules = cf.zones.pagerules.get(zone_id)
    except CloudFlare.exceptions.CloudFlareAPIError as e:
        raise HidoveException(status_code=400, message=e)

    return msg(200, 'success', pagerules)


# 新增页面规则
def do_zone_pagerule_create(cf, zone_id, data):
    try:
        res = cf.zones.pagerules.post(zone_id, data=data)
    except CloudFlare.exceptions.CloudFlareAPIError as e:
        raise HidoveException(status_code=400, message=e)

    return msg(200, 'success', res)


# Page Rule Details
# 获取页面规则详情
@cache()
def get_zone_pagerule_details(cf, zone_id, pagerule_id):
    try:
        pagerule = cf.zones.pagerules.get(zone_id, pagerule_id)
    except CloudFlare.exceptions.CloudFlareAPIError as e:
        raise HidoveException(status_code=400, message=e)

    return msg(200, 'success', pagerule)


#  Update Page Rule
# 更新页面规则
def do_zone_pagerule_update(cf, zone_id, pagerule_id, pagerule):
    try:
        data = {
            'targets': pagerule.targets,
            'actions': pagerule.actions,
            'priority': pagerule.priority,
            'status': pagerule.status,
        }
        res = cf.zones.pagerules.patch(zone_id, pagerule_id, data=data)
    except CloudFlare.exceptions.CloudFlareAPIError as e:
        raise HidoveException(status_code=400, message=e)

    return msg(200, 'success', res)


#  Delete Page Rule
# 删除页面规则
def do_zone_pagerule_delete(cf, zone_id, pagerule_id):
    try:
        pagerule = cf.zones.pagerules.delete(zone_id, pagerule_id)
    except CloudFlare.exceptions.CloudFlareAPIError as e:
        raise HidoveException(status_code=400, message=e)

    return msg(200, 'success', pagerule)


# List Available Page rule setting
# 获取页面规则设置列表
# @cache()
def get_zone_pagerule_setting(cf,zone_id):
    try:
        pagerule = cf.zones.pagerules.settings.get(zone_id)
    except CloudFlare.exceptions.CloudFlareAPIError as e:
        raise HidoveException(status_code=400, message=e)

    return msg(200, 'success', pagerule)
