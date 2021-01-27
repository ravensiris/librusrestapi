import werkzeug

werkzeug.cached_property = werkzeug.utils.cached_property
from flask import Flask, render_template
from api import api, api_blueprint
from flask_talisman import Talisman
from flask_cors import CORS

app = Flask(__name__, static_url_path = "")

# Fix flaskrestplus' inline CSS
# https://stackoverflow.com/questions/58610678/flask-talisman-breaks-flask-restplus-swagger-documentation
SWAGGER_CSP = {
    "script-src": ["'self'", "'unsafe-inline'"],
    "style-src": ["'self'", "'unsafe-inline'"]
}

Talisman(app)
CORS(app)

app.config["RESTPLUS_MASK_SWAGGER"] = False
app.register_blueprint(api_blueprint)

app.view_functions["api.specs"].talisman_view_options = {
    "content_security_policy": SWAGGER_CSP
}
app.view_functions["api.Authentication_authorize_token"].talisman_view_options = {
    "content_security_policy": SWAGGER_CSP
}
app.view_functions["api.Timetable_lesson_units"].talisman_view_options = {
    "content_security_policy": SWAGGER_CSP
}

if __name__ == "__main__":
    app.run(debug=True)
