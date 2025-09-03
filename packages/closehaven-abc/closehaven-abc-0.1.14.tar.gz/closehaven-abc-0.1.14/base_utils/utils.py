import asyncio
import re
from datetime import datetime
from functools import partial, wraps

from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from pydantic import BaseModel


def create_response(message: str, status_code: int, success: bool = False, **kwargs):
    return JSONResponse(
        status_code=status_code,
        content={"success": success, "message": message, **jsonable_encoder(kwargs)},
    )


def create_updated_fields(update_body: BaseModel | dict | None):
    update_fields = {}
    if type(update_body) == dict:
        update_fields = update_body
    elif update_body is not None:
        update_fields = update_body.dict(exclude_none=True, exclude_unset=True)
    update_fields["updated_at"] = datetime.utcnow()
    return update_fields


def validate_name(name):
    if name is None:
        return name
    elif re.search(r"^[a-zA-Z .\-_\d]*$", name) is None:
        raise ValueError(
            "should not contain any special character except -, _, ., and space"
        )
    return name


def async_wrapper(func):
    @wraps(func)
    async def wrapper(*args, loop=None, executor=None, **kwargs):
        if loop is None:
            loop = asyncio.get_event_loop()
        pfunc = partial(func, *args, **kwargs)
        return await loop.run_in_executor(executor, pfunc)

    return wrapper


class Test:
    test = False

    def set_test(value: bool):
        Test.test = value
