import werkzeug

werkzeug.cached_property = werkzeug.utils.cached_property
from flask import Flask
from api import api_blueprint
from flask_talisman import Talisman
from flask_cors import CORS

app = Flask(__name__, static_url_path = "")

Talisman(app)
CORS(app)

app.config["RESTX_MASK_SWAGGER"] = False
app.register_blueprint(api_blueprint)

if __name__ == "__main__":
    app.run(debug=True)
