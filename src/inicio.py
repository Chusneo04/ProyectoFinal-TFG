from flask import Blueprint, render_template, request
from flask_login import current_user

inicio_bp = Blueprint('inicio', __name__)


@inicio_bp.route('/')
def index():
    return render_template('index.html')

