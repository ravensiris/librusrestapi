from flask_restx import Namespace, fields, Resource
from flask import request
from librusapi.timetable import lesson_units, LessonUnit
from librusapi.token import Token
from typing import Dict, Any
from librusapi.exceptions import AuthorizationError
from api.api import (
    DefaultModel,
    ErrorResponse,
    FailResponse,
    SuccessResponse,
    SuccessModel,
    data_wrap,
    ErrorModel,
)
from isoweek import Week
from datetime import datetime

api = Namespace("Timetable", path="/timetable")

LessonUnitModel = api.model(
    "LessonUnit",
    dict(
        name=fields.String(example="Math", required=True),
        teacher=fields.String(example="John Doe", required=True),
        classroom=fields.String(example="111"),
        info=fields.String(
            description="Additional info attached to a lesson unit.",
            example="Cancelled",
        ),
        start=fields.DateTime(required=True),
        duration=fields.Integer(
            description="Total seconds.", example=2700, required=True
        ),
    ),
)

api.models[SuccessModel.name] = SuccessModel
api.models[ErrorModel.name] = ErrorModel

LessonUnitsModel = api.inherit(
    "LessonUnitsModel",
    SuccessModel,
    data_wrap(
        api,
        "UnitsData",
        units=fields.List(fields.Nested(LessonUnitModel), required=True),
        week=fields.String(
            description="ISO format week date", required=True, example="2011W08"
        ),
    ),
)

LessonUnitFailModel = api.model(
    "LessonUnitFailModel ",
    data_wrap(
        api,
        "LessonUnitFail",
        week=fields.String(example="week path variable must be a proper ISO week date"),
        token=fields.String(example="malformed token"),
    ),
)


def serialize_unit(lesson_unit: LessonUnit) -> Dict[str, Any]:
    lu = lesson_unit.__dict__
    lu["start"] = lesson_unit.start.isoformat()
    lu["duration"] = lesson_unit.duration.total_seconds()
    return lu


@api.route("/units")
@api.route("/units/<string:week>")
@api.doc(security="apikey")
@api.header("X-API-KEY", "token", required=True)
class LessonUnits(Resource):
    @api.response(200, "Success", LessonUnitsModel)
    @api.response(403, "Token invalid", ErrorModel)
    @api.response(401, "Unauthorized", ErrorModel)
    @api.response(400, "Bad Request", LessonUnitFailModel)
    @api.marshal_with(DefaultModel, skip_none=True)
    def get(_, week=None):
        # Make your own library for ISO week parsing. this one sucks
        if not week:
            week = Week.withdate(datetime.now())
        else:
            try:
                ws = week.split("-")
                if len(ws) == 3:
                    week = "".join(ws[0:-1])
                week = Week.fromstring(week)
            except ValueError:
                return (
                    FailResponse(
                        week="week path variable must be a proper ISO week date"
                    ),
                    400,
                )
        try:
            token = Token(request.headers.get("X-API-KEY"))
        except:
            return FailResponse(token="malformed token"), 400
        units = []
        if token:
            try:
                monday = datetime.combine(week.monday(), datetime.min.time())
                units = lesson_units(token, monday)
                units = list(map(serialize_unit, units))
                return SuccessResponse(units=units, week=week.isoformat())
            except AuthorizationError as e:
                return ErrorResponse(str(e)), 403
        else:
            return ErrorResponse("Unauthorized"), 401