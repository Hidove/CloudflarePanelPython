from typing import Optional

import CloudFlare
import requests
from pydantic import Field
from pydantic.main import BaseModel

from App import HidoveException
from App.utils.common import msg
from App.ext import memorize_cache as cache


class Dns_record(BaseModel):
    name: str
    type: str
    content: str
    proxied: Optional[bool] = Field(
        None, title="是否启用CDN"
    )
    ttl: Optional[int] = 1


# 获取域名列表
@cache()
def get_zones(cf):
    try:
        zones_get = cf.zones.get()
    except CloudFlare.exceptions.CloudFlareAPIError as e:
        raise HidoveException(status_code=400, message=e)

    return msg(200, 'success', zones_get)


# 获取域名dns解析解析记录
@cache()
def get_dns_records(cf, zone_id: str):
    try:
        dns_records = cf.zones.dns_records.get(zone_id)

    except CloudFlare.exceptions.CloudFlareAPIError as e:
        raise HidoveException(status_code=400, message=e)

    return msg(200, 'success', dns_records)


# 获取记录信息
@cache()
def get_dns_record_info(cf, zone_id: str, dns_record_id: str):
    try:
        dns_record_info = cf.zones.dns_records.get(zone_id, dns_record_id)
    except CloudFlare.exceptions.CloudFlareAPIError as e:
        raise HidoveException(status_code=400, message=e)

    return msg(200, 'success', dns_record_info)


# 获取域名信息
@cache()
def get_zone_info(cf, zone_name: str = None, zone_id: str = None):
    try:
        if zone_name:
            zone_info = cf.zones.get(params={
                'name': zone_name,
                'match': 'all'
            })
        else:
            zone_info = cf.zones.get(identifier1=zone_id, params={
                'match': 'all'
            })
    except CloudFlare.exceptions.CloudFlareAPIError as e:
        raise HidoveException(status_code=400, message=e)
    info = {}
    if type(zone_info) == dict:
        info = zone_info
    elif zone_info:
        info = zone_info.pop()
    else:
        raise HidoveException(status_code=400,
                              message='This zone was not found')

    return msg(200, 'success', info)


# 新增记录
def do_dns_record_create(cf, zone_id, dns_record: Dns_record):
    if dns_record.ttl == None:
        dns_record.ttl = 1
    dns_record = {
        'name': dns_record.name,
        'type': dns_record.type,
        'content': dns_record.content,
        'proxied': dns_record.proxied,
        'ttl': dns_record.ttl,
    }
    try:
        res = cf.zones.dns_records.post(zone_id, data=dns_record)
    except CloudFlare.exceptions.CloudFlareAPIError as e:
        raise HidoveException(status_code=400,
                              message='/zones.dns_records.post %s - %d %s - api call failed' % (
                                  dns_record.get('name'), e, e))

    return msg(200, 'success', res)


# 更新记录
def do_dns_record_update(cf, zone_id, dns_record_id, dns_record: Dns_record):
    data = {
        'name': dns_record.name,
        'type': dns_record.type,
        'content': dns_record.content,
        'proxied': dns_record.proxied,
        'ttl': int(dns_record.ttl),
    }

    try:
        res = cf.zones.dns_records.put(zone_id, dns_record_id, data=data)
    except CloudFlare.exceptions.CloudFlareAPIError as e:
        raise HidoveException(status_code=400,
                              message='/zones.dns_records.put %s - %d %s - api call failed' % (dns_record_id, e, e))

    return msg(200, 'success', res)


# 删除域名记录
def do_dns_record_delete(cf, zone_id, dns_record_id):
    try:
        res = cf.zones.dns_records.delete(zone_id, dns_record_id)
    except CloudFlare.exceptions.CloudFlareAPIError as e:
        raise HidoveException(status_code=400,
                              message='/zones.dns_records.delete %s - %d %s - api call failed' % (dns_record_id, e, e))
    return msg(200, 'success', res)


# 删除域名
def do_zone_delete(cf, zone_id):
    try:
        res = cf.zones.delete(zone_id)
    except CloudFlare.exceptions.CloudFlareAPIError as e:
        raise HidoveException(status_code=400, message='/zones.delete %s - %d %s - api call failed' % (zone_id, e, e))

    return msg(200, 'success', res)


# 添加域名
def do_zone_create(host_key: str, user_key: str, zone_name: str):
    try:
        requests_post = requests.post(
            'https://api.cloudflare.com/host-gw.html',
            {
                'act': 'zone_set',
                'host_key': host_key,
                'user_key': user_key,
                'zone_name': zone_name,
                'resolve_to': 'hidove.cn',
                'subdomains': '@,www',
            })
        res_json = requests_post.json()
        if res_json.get('result') == 'success':
            return msg(200, 'success', res_json.get('response'))
        raise HidoveException(status_code=400, message=res_json.get('msg'))
    except Exception as e:
        raise HidoveException(status_code=400, message=e)


# 清理缓存 (全系通用)
def do_cache_purge(cf, zone_id, params):
    try:
        if (params.files != []):
            data = {
                'files': params.files,
            }
        elif (params.purge_everything == True):
            data = {
                'purge_everything': True,
            }
        else:
            raise HidoveException(status_code=400,
                                  message='The purge_everything and the files can\'t be empty at the same time!')


        res = cf.zones.purge_cache.post(zone_id, data=data)

    except CloudFlare.exceptions.CloudFlareAPIError as e:
        raise HidoveException(status_code=400,
                              message='/zones.purge_cache.post %s - %d %s - api call failed' % (zone_id, e, e))

    except Exception as e:
        raise HidoveException(status_code=400, message=e)

    return msg(200, 'success', res)
