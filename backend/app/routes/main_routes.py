from flask import Blueprint, render_template, current_app
import os

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    try:
        return render_template('index.html')
    except Exception as e:
        current_app.logger.error(f"Error rendering template: {str(e)}")
        current_app.logger.info(f"Current working directory: {os.getcwd()}")
        current_app.logger.info(f"Template folder: {current_app.template_folder}")
        current_app.logger.info(f"Available templates: {os.listdir(current_app.template_folder)}")
        raise