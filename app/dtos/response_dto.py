from starlette.responses import JSONResponse
from typing import List, Optional


def api_response(status: int, message: str = None, data: Optional[dict | List] = None):
    return JSONResponse(
        status_code=status,
        content={
            "status": status,
            "message": message,
            "data": data or None
        }
    )