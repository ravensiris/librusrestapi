from enum import EnumMeta
from typing import Any, Dict, cast, Literal
from dataclasses import dataclass
from flask_restx import Model, fields


class Status(EnumMeta):
    SUCCESS: Literal["success"] = "success"
    FAIL: Literal["fail"] = "fail"
    ERROR: Literal["error"] = "error"


@dataclass
class Response:
    status: Status


class SuccessResponse(Response):
    def __init__(self, **values: Any) -> None:
        super().__init__(cast(Status, Status.SUCCESS))
        self.data = values


class FailResponse(Response):
    def __init__(self, **values: str) -> None:
        super().__init__(cast(Status, Status.FAIL))
        self.data = values


class ErrorResponse(Response):
    def __init__(self, message: str) -> None:
        super().__init__(cast(Status, Status.ERROR))
        self.message = message

class StatusField(fields.Raw):
    __schema_type__ = "success | fail | error"
    __schema_example__ = "success"

    def format(self, value: Status):
        return str(value)


def data_wrap(api, fieldname, **data: fields.Raw):
    field = api.model(fieldname + "Field", data)
    return dict(data=fields.Nested(field))

DefaultModel = Model(
    "DefaultModel",
    dict(
        status=StatusField(),
        data=fields.Raw(),
        message=fields.String()
    )
)

SuccessModel = Model("SuccessModel", dict(status=StatusField(default=Status.SUCCESS), data=fields.Raw()))

ErrorModel = Model(
    "ErrorModel",
    dict(
        status=StatusField(default=Status.ERROR, example=Status.ERROR),
        message=fields.String,
    ),
)