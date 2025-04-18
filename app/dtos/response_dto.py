from starlette.responses import JSONResponse


def api_response(status: int, message: str = None, data: dict = None):
    return JSONResponse(
        status_code=status,
        content={
            "status": status,
            "message": message,
            "data": data or None
        }
    )