from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import Any, Optional, Union


class ResponseCode:
    SUCCESS = 0
    ERROR = -1


class ResponseMessage:
    SUCCESS = 'success'
    ERROR = 'error'


def default_data():
    return ''


class BaseResponse(BaseModel):
    code: int = Field(0, description='API status code')
    message: str = Field('success', description='API status message')
    data: Optional[Union[Any, None]] = Field(default_factory=default_data, description='API data')

    class Config:
        json_schema_extra = {
            'example': {
                'code': ResponseCode.SUCCESS,
                'message': ResponseMessage.SUCCESS,
                'data': None
            }
        }

    @classmethod
    def success(cls, data: Optional[Any] = '', message: str = ResponseMessage.SUCCESS, code=ResponseCode.SUCCESS):
        return BaseResponse(code=code, message=message, data=data)

    @classmethod
    def error(cls, data: Optional[Any] = '', message: str = ResponseMessage.ERROR, code=ResponseCode.ERROR):
        return BaseResponse(code=code, message=message, data=data)

    @classmethod
    def json_resp(cls, data=None, status_code: int = 200):
        if data is None:
            data = {}
        return JSONResponse(status_code=status_code, content=data)
