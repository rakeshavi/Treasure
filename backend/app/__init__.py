from flask import Flask
from app.config import Config
import logging
import os

def create_app():
    app = Flask(__name__, 
                template_folder=os.path.abspath(os.path.join(os.path.dirname(__file__), 'templates')))
    app.config.from_object(Config)

    # Configure logging
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    from app.routes import plaid_bp, main_bp
    app.register_blueprint(plaid_bp, url_prefix='/api/plaid')
    app.register_blueprint(main_bp)

    return app