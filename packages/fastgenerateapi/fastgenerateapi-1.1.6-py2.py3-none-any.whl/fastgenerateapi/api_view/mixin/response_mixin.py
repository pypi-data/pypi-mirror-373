import time
from io import BytesIO
from typing import Union, Optional, Dict, Any
from urllib.parse import quote

from fastapi import HTTPException
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel

from fastgenerateapi.settings.all_settings import settings
from starlette.background import BackgroundTask
from starlette.responses import JSONResponse, Response, StreamingResponse

from fastgenerateapi.pydantic_utils.base_model import JSON_ENCODERS
from fastgenerateapi.schemas_factory import response_factory


class ResponseMixin:

    @staticmethod
    def success(
            msg: str = "请求成功",
            status_code: int = 200,
            code: Optional[int] = None,
            data: Union[BaseModel, dict, str, None] = None,
            background: Optional[BackgroundTask] = None,
            *args,
            **kwargs
    ):
        if data is None:
            json_compatible_data = {}
        else:
            json_compatible_data = jsonable_encoder(data, custom_encoder=JSON_ENCODERS)
        if code is None:
            code = settings.app_settings.CODE_SUCCESS_DEFAULT_VALUE
        resp = response_factory()(**{
            "success": True,
            "code": code,
            settings.app_settings.MESSAGE_RESPONSE_FIELD: msg,
            "data": json_compatible_data
        })
        kwargs.update(resp.dict())
        return JSONResponse(kwargs, status_code=status_code, background=background)

    @staticmethod
    def fail(
            msg: str = "请求失败",
            status_code: int = 200,
            code: Optional[int] = None,
            # success: bool = False,
            data: Union[BaseModel, dict, str, None] = None,
            background: Optional[BackgroundTask] = None,
            headers: Optional[Dict[str, Any]] = None,
            *args,
            **kwargs,
    ):

        if data is None:
            json_compatible_data = {}
        else:
            json_compatible_data = jsonable_encoder(data, custom_encoder=JSON_ENCODERS)
        if code is None:
            code = settings.app_settings.CODE_FAIL_DEFAULT_VALUE
        resp = response_factory()(**{
            "success": False,
            "code": code,
            settings.app_settings.MESSAGE_RESPONSE_FIELD: msg,
            "data": json_compatible_data
        })
        kwargs.update(resp.dict())
        return JSONResponse(
            kwargs,
            status_code=status_code,
            headers=headers or {"Access-Control-Allow-Origin": '*'},
            background=background
        )

    @staticmethod
    def error(
            msg: str = "系统繁忙，请稍后再试...",
            status_code: int = 400,
            headers: Optional[Dict[str, Any]] = None,
            *args,
            **kwargs,
    ):

        raise HTTPException(
            status_code=status_code,
            detail=msg,
            headers=headers or {"Access-Control-Allow-Origin": '*'},
        )

    @staticmethod
    def stream(
            bytes_io: BytesIO,
            file_name: Optional[str] = None,
            media_type: Optional[str] = None,
            is_xlsx: Optional[bool] = None,
            is_docx: Optional[bool] = None,
            is_pdf: Optional[bool] = None,
    ) -> StreamingResponse:
        """

        :param bytes_io: io.BytesIO()
        :param file_name: 文件名称
        :param media_type: 优先度大于其他参数
        :param is_xlsx: 自动设置media_type
        :param is_docx: 自动设置media_type
        :param is_pdf: 自动设置media_type
        :return:  StreamingResponse
        """

        if not media_type:
            if is_xlsx:
                media_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;charset=UTF-8"
            elif is_docx:
                media_type = "application/vnd.openxmlformats-officedocument.wordprocessingml.document;charset=UTF-8"
            elif is_pdf:
                media_type = "application/pdf"
        headers = {}
        if file_name:
            headers["Content-Disposition"] = f"attachment; filename={quote(file_name, safe='/:?=&')}"
        return StreamingResponse(
            bytes_io,
            media_type= media_type,
            headers=headers,
        )
