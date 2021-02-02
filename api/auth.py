from flask_restx import Namespace, fields, Resource
from flask import request
from librusapi.token import get_token
from librusapi.exceptions import AuthorizationError
from api.api import ErrorResponse, SuccessResponse, ErrorModel, SuccessModel, data_wrap, DefaultModel

api = Namespace("Authentication", path="/auth")

api.models[DefaultModel.name] = DefaultModel
api.models[ErrorModel.name] = ErrorModel
api.models[SuccessModel.name] = SuccessModel
TokenModel = api.inherit(
    "TokenModel",
    SuccessModel,
    data_wrap(
        api,
        "Token",
        token=fields.String(example="L00-00000000000000000000000000000000", required=True),
    ),
)


@api.route("/")
class AuthorizeToken(Resource):
    @api.doc(security="Authorization Basic")
    @api.header(
        "Authorization", "Authorization: Basic base64(username:password)", required=True
    )
    @api.response(200, "Success", TokenModel)
    @api.response(400, "Validation Error", ErrorModel)
    @api.response(401, "Authorization Error", ErrorModel)
    @api.marshal_with(DefaultModel, skip_none=True)
    def get(_):
        auth = request.authorization
        if auth and auth.type == "basic":
            try:
                token = get_token(auth.username, auth.password)
                return SuccessResponse(token=token), 200
            except AuthorizationError as e:
                return ErrorResponse(str(e)), 401
        else:
            return ErrorResponse("Provide a proper 'Authorization' header"), 400
