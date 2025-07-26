from flask import Flask
from flask_cors import CORS
from .routes import routes
from .db import init_db

def create_app():
    app = Flask(__name__)

    # ✅ Must match frontend origin exactly (localhost:5173)
    CORS(app, origins=["http://localhost:5173","https://eatlater.netlify.app"])  # Removed supports_credentials


    init_db()
    app.register_blueprint(routes, url_prefix='/api')
    return app
