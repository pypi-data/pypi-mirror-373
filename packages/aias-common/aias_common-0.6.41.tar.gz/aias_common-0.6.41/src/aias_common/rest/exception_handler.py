from typing import Callable, TypeAlias

from fastapi import status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from starlette.requests import Request

from aias_common.rest.exception import OGCException, RESTException

HandledExceptions: TypeAlias = RequestValidationError | OGCException


class ExceptionHandler(BaseModel, arbitrary_types_allowed=True):
    exception: type[Exception]
    handler: Callable[[Request, HandledExceptions], JSONResponse]


def validation_exception_handler(req: Request, exc: RequestValidationError):
    # Format the detail of the error message
    detail = ""
    for error in exc.errors():
        if len(error["loc"]) > 1:
            loc = error["loc"][1]
            for i in range(2, len(error["loc"])):
                if isinstance(error["loc"][i], str):
                    loc += f'.{error["loc"][i]}'
                elif isinstance(error["loc"][i], int):
                    loc += f'[{str(error["loc"][i])}]'
            detail += f'{loc}: {error["msg"]}\n'
        elif len(error["loc"]) > 0:
            detail += f'{error["loc"][0]}: {error["msg"]}\n'
    detail = detail[:-1]

    return JSONResponse(content=RESTException(
            type="bad request",
            status=status.HTTP_422_UNPROCESSABLE_ENTITY,
            title="validation error",
            detail=detail,
            instance=str(req.url)).model_dump(exclude_none=True, exclude_unset=True),
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY)


def server_error_handler(req: Request, exc: OGCException):
    return JSONResponse(content=RESTException(
            type=exc.type,
            status=exc.status,
            title=exc.title,
            detail=exc.detail,
            instance=str(req.url)).model_dump(exclude_none=True, exclude_unset=True),
        status_code=exc.status if exc.status is not None
        else status.HTTP_500_INTERNAL_SERVER_ERROR)


EXCEPTION_HANDLERS: list[ExceptionHandler] = [
    ExceptionHandler(exception=RequestValidationError,
                     handler=validation_exception_handler),
    ExceptionHandler(exception=OGCException,
                     handler=server_error_handler)
]
