from fastapi import Request, HTTPException
from fastapi.exceptions import RequestValidationError
from starlette.status import HTTP_500_INTERNAL_SERVER_ERROR, HTTP_400_BAD_REQUEST
from starlette.exceptions import HTTPException as StarletteHTTPException
from app.dtos.response_dto import api_response
from app.exceptions.exceptions import UserAlreadyExistsException


async def custom_http_exception_handler(request: Request, exc: StarletteHTTPException):
    """
    catch HttpException like 401, 404, 500 etc
    :param request:
    :param exc:
    :return: api_response
    """
    print("== custom_http_exception_handler called ==")
    print("Type:", type(exc))
    print("Cause:", repr(exc.__cause__))
    print("Context:", repr(exc.__context__))
    # HTTPException wraps custom Exception class. Therefore, check __context__
    if isinstance(exc.__context__, UserAlreadyExistsException):
        return api_response(
            status=HTTP_400_BAD_REQUEST,
            message=str(exc.__context__)
        )

    return api_response(status=exc.status_code, message=exc.detail, data=None)


async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """
    catch validation error
    :param request:
    :param exc:
    :return: api_response
    """
    print("== validation_exception_handler called ==")
    error_messages: list[str] = [error["msg"] for error in exc.errors()]
    first_message: str = error_messages[0] if error_messages else "Validation error"

    return api_response(status=422, message=first_message, data=error_messages)


async def general_exception_handler(request: Request, exc: Exception):
    """
    other unexpected errors
    :param request:
    :param exc:
    :return:
    """
    return api_response(status=HTTP_500_INTERNAL_SERVER_ERROR, message=str(exc), data=None)


