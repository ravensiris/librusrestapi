from flask_restx import Api
from flask import Blueprint
from api.auth import api as auth_api
from api.timetable import api as timetable_api

authorizations = {
    "apikey": {"type": "apiKey", "in": "header", "name": "X-API-KEY"},
    "Authorization Basic": {"type": "basic", "in": "header", "name": "Authorization"},
}
api_blueprint = Blueprint("api", __name__, url_prefix="/api")
api = Api(api_blueprint, authorizations=authorizations)
api.add_namespace(auth_api)
api.add_namespace(timetable_api)
