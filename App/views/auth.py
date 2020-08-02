from datetime import timedelta

from fastapi import APIRouter, Depends
import requests
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel

from App import HidoveException
from App.ext import create_access_token
from App.response import dict_response
from App.utils.common import msg, get_setting

router = APIRouter()

setting = get_setting()


class Item(BaseModel):
    email: str
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str


@router.post("/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    requests_post = requests.post(
        'https://api.cloudflare.com/host-gw.html',
        {
            'act': 'user_auth',
            'host_key': setting.HOST_KEY,
            'cloudflare_email': form_data.username,
            'cloudflare_pass': form_data.password,
        })
    res_json = requests_post.json()
    if res_json.get('result') != 'success':
        raise HidoveException(status_code=400, message=res_json.get('msg'), data=res_json)
    access_token_expires = timedelta(minutes=setting.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data=res_json.get('response'), expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/register", response_model=dict_response)
async def register(Item: Item):
    requests_post = requests.post(
        'https://api.cloudflare.com/host-gw.html',
        {
            'act': 'user_create',
            'host_key': setting.HOST_KEY,
            'cloudflare_email': Item.email,
            'cloudflare_pass': Item.password,
        })

    res_json = requests_post.json()
    if res_json.get('result') != 'success':
        raise HidoveException(status_code=400, message=res_json.get('msg'), data=res_json)
    return msg(200, 'success')
