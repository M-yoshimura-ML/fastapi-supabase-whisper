from fastapi import Request, HTTPException
from fastapi.exceptions import RequestValidationError
from starlette.status import HTTP_500_INTERNAL_SERVER_ERROR

from app.dtos.response_dto import api_response


async def custom_http_exception_handler(request: Request, exc: HTTPException):
    """
    catch HttpException like 401, 404, 500 etc
    :param request:
    :param exc:
    :return: api_response
    """
    return api_response(status=exc.status_code, message=exc.detail, data=None)


async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """
    catch validation error
    :param request:
    :param exc:
    :return: api_response
    """
    return api_response(status=422, message="Validation error", data=exc.errors())


async def general_exception_handler(request: Request, exc: Exception):
    """
    other unexpected errors
    :param request:
    :param exc:
    :return:
    """
    return api_response(status=HTTP_500_INTERNAL_SERVER_ERROR, message=str(exc), data=None)
