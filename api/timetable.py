from flask_restx import Namespace, fields, Resource
from flask import request
from librusapi.timetable import lesson_units, LessonUnit
from typing import Dict, Any
from librusapi.exceptions import AuthorizationError
from api.api import DefaultModel, ErrorResponse, SuccessResponse, SuccessModel, data_wrap, ErrorModel

api = Namespace("Timetable", path="/timetable")

LessonUnitModel = api.model(
    "LessonUnit",
    dict(
        name=fields.String(example="Math"),
        teacher=fields.String(example="John Doe"),
        classroom=fields.String(example="111"),
        info=fields.String(description="Additional info attached to a lesson unit.", example="Cancelled"),
        start=fields.DateTime(),
        duration=fields.Integer(description="Total seconds.", example=2700),
    ),
)

api.models[SuccessModel.name] = SuccessModel
api.models[ErrorModel.name] = ErrorModel

LessonUnitsModel = api.inherit(
    "LessonUnitsModel",
    SuccessModel,
    data_wrap(api, 'Units', units=fields.List(fields.Nested(LessonUnitModel)))
)

def serialize_unit(lesson_unit: LessonUnit) -> Dict[str, Any]:
    lu = lesson_unit.__dict__
    lu["start"] = lesson_unit.start.isoformat()
    lu["duration"] = lesson_unit.duration.total_seconds()
    return lu


@api.route("/units")
@api.doc(security="apikey")
@api.header("X-API-KEY", "DZIENNIKSID", required=True)
class LessonUnits(Resource):
    @api.response(200, "Success", LessonUnitsModel)
    @api.response(403, "Token invalid", ErrorModel)
    @api.response(401, "Unauthorized", ErrorModel)
    @api.marshal_with(DefaultModel, skip_none=True)
    def get(self):
        token = request.headers.get("X-API-KEY")
        units = []
        if token:
            try:
                units = list(map(serialize_unit, lesson_units(token)))
                return SuccessResponse(units=units)
            except AuthorizationError as e:
                return ErrorResponse(str(e)), 403
        else:
            return ErrorResponse("Unauthorized"), 401