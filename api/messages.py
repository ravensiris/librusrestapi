from dataclasses import field
from flask_restx import Namespace, fields, Resource
from api.api import (
    DefaultModel,
    ErrorResponse,
    FailResponse,
    SuccessResponse,
    SuccessModel,
    data_wrap,
    ErrorModel,
)
from librusapi.token import Token
from flask import request
from librusapi.messages import list_messages, MessageBrief

api = Namespace("Messages")

MessageBriefModel = api.model(
    "MessageBrief",
    dict(
        id=fields.String(example="12345789", required=True),
        title=fields.String(example="Welcome to Blueberry High!", required=True),
        sender=fields.String(example="John Doe", required=True),
        sent=fields.DateTime(required=True),
        has_attachment=fields.Boolean(required=True),
        is_read=fields.Boolean(required=True),
    ),
)

PageInfoModel = api.model(
    "PageInfo",
    dict(
        current=fields.Integer(example=0, required=True),
        max_page=fields.Integer(example=1, required=True),
    ),
)


api.models[SuccessModel.name] = SuccessModel
api.models[ErrorModel.name] = ErrorModel

ListMessagesModel = api.inherit(
    "ListMessagesModel",
    SuccessModel,
    data_wrap(
        api,
        "ListMessagesData",
        messages=fields.List(fields.Nested(MessageBriefModel)),
        pageInfo=fields.Nested(PageInfoModel)
    ),
)

ListMessagesFailModel = api.model(
    "ListMessagesFailModel",
    data_wrap(
        api,
        "ListMessagesFail",
        token=fields.String(example="malformed token", required=True),
        page=fields.Integer(example="page out of bounds", required=True),
    ),
)


def serialize_msg_brief(message: MessageBrief):
    msg = message.__dict__
    msg["sent"] = message.sent.isoformat()
    return msg


@api.route("/units/<int:page>")
@api.doc(security="apikey")
@api.header("X-API-KEY", "token", required=True)
class LessonUnits(Resource):
    @api.response(200, "Success", ListMessagesModel)
    @api.response(403, "Token invalid", ErrorModel)
    @api.response(401, "Unauthorized", ErrorModel)
    @api.response(400, "Bad Request", ListMessagesFailModel)
    @api.marshal_with(DefaultModel, skip_none=True)
    def get(_, page: int):
        try:
            token = Token(request.headers.get("X-API-KEY"))
        except:
            return FailResponse(token="malformed token"), 400
        try:
            info, msgs = list_messages(token, page)
            msgs = list(map(serialize_msg_brief, msgs))
            return SuccessResponse(pageInfo=info.__dict__, messages=msgs)
        except Exception as e:
            # TODO: Proper error handling
            return ErrorResponse(str(e)), 400
