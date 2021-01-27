import werkzeug

werkzeug.cached_property = werkzeug.utils.cached_property
from flask import Flask, render_template
from api import api, api_blueprint
from flask_talisman import Talisman
from flask_cors import CORS

app = Flask(__name__, static_url_path = "")
Talisman(app)
CORS(app)


if __name__ == "__main__":
    app.config["RESTPLUS_MASK_SWAGGER"] = False
    app.register_blueprint(api_blueprint)
    app.run()
