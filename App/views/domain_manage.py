import inspect
from typing import List

import CloudFlare

from fastapi import APIRouter, Depends, Body
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel

from App import ext
from App.response import list_response, dict_response
from App.utils import dns, zone_setting
from App.utils.common import get_setting

router = APIRouter()

setting = get_setting()


class zone(BaseModel):
    zone_name: str


class purge(BaseModel):
    purge_everything: bool = False
    files: list = []


class zone_setting_model(BaseModel):
    id: str
    value: str


class zone_settings(BaseModel):
    data: List[zone_setting_model]


class pagerule_model(BaseModel):
    targets: list
    actions: list
    priority: int
    status: str


class Token(BaseModel):
    access_token: str
    token_type: str


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")


def get_current_user_cf(token: str = Depends(oauth2_scheme)):
    user = ext.get_current_user(token)
    return CloudFlare.CloudFlare(
        email=user.get('cloudflare_email'),
        token=user.get('user_api_key'),
        debug=setting.DEBUG
    )


def get_current_user(token: str = Depends(oauth2_scheme)):
    return ext.get_current_user(token)


def get_current_key(cf):
    return inspect.stack()[1][3] + cf._base.email


# 获取域名列表

@router.get('/zone_list', response_model=list_response)
async def get_zones(cf: CloudFlare.CloudFlare = Depends(get_current_user_cf)):
    return dns.get_zones(cf)


# 获取域名dns解析解析记录
@router.get('/get_dns_records', response_model=list_response)
async def get_dns_records(zone_id: str, cf: CloudFlare.CloudFlare = Depends(get_current_user_cf)):
    return dns.get_dns_records(cf, zone_id)


# 获取记录信息
@router.get('/get_dns_record_info', response_model=dict_response)
async def get_dns_record_info(zone_id: str, dns_record_id: str,
                              cf: CloudFlare.CloudFlare = Depends(get_current_user_cf)):
    return dns.get_dns_record_info(cf, zone_id, dns_record_id)


# 获取域名信息
@router.get('/get_zone_info', response_model=dict_response)
async def get_zone_info(zone_name: str = None, zone_id: str = None,
                        cf: CloudFlare.CloudFlare = Depends(get_current_user_cf)):
    return dns.get_zone_info(cf, zone_name, zone_id)


# 新增记录
@router.post('/do_dns_record_create', response_model=dict_response)
async def do_dns_record_create(zone_id: str, dns_record: dns.Dns_record,
                               cf: CloudFlare.CloudFlare = Depends(get_current_user_cf)):
    return dns.do_dns_record_create(
        cf, zone_id, dns_record)


# 更新记录
@router.put('/do_dns_record_update', response_model=dict_response)
async def do_dns_record_update(zone_id: str, dns_record_id: str, dns_record: dns.Dns_record,
                               cf: CloudFlare.CloudFlare = Depends(get_current_user_cf)):
    return dns.do_dns_record_update(
        cf, zone_id, dns_record_id, dns_record)


# 删除记录
@router.delete('/do_dns_record_delete', response_model=dict_response)
async def do_dns_record_delete(zone_id: str, dns_record_id: str,
                               cf: CloudFlare.CloudFlare = Depends(get_current_user_cf)):
    return dns.do_dns_record_delete(
        cf, zone_id, dns_record_id)


# 删除域名
@router.delete('/do_zone_delete', response_model=dict_response)
async def do_zone_delete(zone_id: str, cf: CloudFlare.CloudFlare = Depends(get_current_user_cf)):
    return dns.do_zone_delete(cf, zone_id)


# 新增域名
@router.post('/do_zone_create', response_model=dict_response)
async def do_zone_create(zone: zone, user=Depends(get_current_user),
                         cf: CloudFlare.CloudFlare = Depends(get_current_user_cf)):
    return dns.do_zone_create(cf, setting.HOST_KEY, user.get('user_key'), zone.zone_name)


# 清理缓存
@router.post('/do_cache_purge', response_model=dict_response)
async def do_cache_purge(zone_id: str, params: purge, cf: CloudFlare.CloudFlare = Depends(get_current_user_cf)):
    return dns.do_cache_purge(cf, zone_id, params)


# 获取域名所有设置
@router.get('/get_all_zone_settings', response_model=list_response)
async def get_all_zone_settings(zone_id: str, cf: CloudFlare.CloudFlare = Depends(get_current_user_cf)):
    return zone_setting.get_all_zone_settings(cf, zone_id)


# 获取域名目标设置
@router.get('/get_zone_setting', response_model=list_response)
async def get_all_zone_settings(zone_id: str, cf: CloudFlare.CloudFlare = Depends(get_current_user_cf)):
    return zone_setting.get_all_zone_settings(cf, zone_id)


# 批量更新域名设置
@router.patch('/do_zone_settings_update', response_model=list_response)
async def do_zone_settings_update(zone_id: str, data: zone_settings,
                                  cf: CloudFlare.CloudFlare = Depends(get_current_user_cf)):
    return zone_setting.do_zone_settings_update(cf, zone_id, data)


# 更新域名目标设置
@router.patch('/do_zone_setting_update', response_model=dict_response)
async def do_zone_setting_update(zone_id: str, type: str, value=Body(..., embed=True),
                                 cf: CloudFlare.CloudFlare = Depends(get_current_user_cf)):
    return zone_setting.do_zone_setting_update(cf, zone_id, type, value)


# 获取页面规则
@router.get('/get_zone_pagerules', response_model=list_response)
async def get_zone_pagerules(zone_id: str, cf: CloudFlare.CloudFlare = Depends(get_current_user_cf)):
    return zone_setting.get_zone_pagerules(cf, zone_id)


# 获取页面规则设置列表
@router.get('/get_zone_pagerule_setting', response_model=list_response)
async def get_zone_pagerule_setting(zone_id: str, cf: CloudFlare.CloudFlare = Depends(get_current_user_cf)):
    return zone_setting.get_zone_pagerule_setting(cf, zone_id)


# 新增页面规则
@router.post('/do_zone_pagerule_create', response_model=list_response)
async def do_zone_pagerule_create(zone_id: str, data: pagerule_model,
                                  cf: CloudFlare.CloudFlare = Depends(get_current_user_cf)):
    return zone_setting.do_zone_pagerule_create(cf, zone_id, data)


# 删除页面规则
@router.delete('/do_zone_pagerule_delete', response_model=list_response)
async def do_zone_pagerule_delete(zone_id: str, pagerule_id: str,
                                  cf: CloudFlare.CloudFlare = Depends(get_current_user_cf)):
    return zone_setting.do_zone_pagerule_delete(cf, zone_id, pagerule_id)


# 获取页面规则详情
@router.get('/get_zone_pagerule_details', response_model=list_response)
async def get_zone_pagerule_details(zone_id: str, pagerule_id: str,
                                    cf: CloudFlare.CloudFlare = Depends(get_current_user_cf)):
    return zone_setting.get_zone_pagerule_details(cf, zone_id, pagerule_id)


# 更新页面规则
@router.put('/do_zone_pagerule_update', response_model=dict_response)
async def do_zone_pagerule_update(
        zone_id: str, pagerule_id: str, data: pagerule_model,
        cf: CloudFlare.CloudFlare = Depends(get_current_user_cf)):
    return zone_setting.do_zone_pagerule_update(cf, zone_id, pagerule_id, data)
