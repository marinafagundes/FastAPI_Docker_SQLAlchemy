from fastapi import Request
from fastapi.responses import JSONResponse

from shared.exceptions import NotFound


async def not_found_exception_handler(request: Request, exc: NotFound):
    resource_name = exc.name or "Recurso"
    return JSONResponse(
        status_code=404,
        content={
            "message": f"Oops! {resource_name} não encontrado(a).",
            "path": request.url.path,
        },
    )
