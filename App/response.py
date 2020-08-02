from pydantic import BaseModel


class list_response(BaseModel):
    code: int = 200
    msg: str = 'success'
    data: list = []


class dict_response(BaseModel):
    code: int = 200
    msg: str = 'success'
    data: dict = []
