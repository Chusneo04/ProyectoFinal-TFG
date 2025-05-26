from flask import Blueprint, render_template, request
from flask_login import current_user

inicio_bp = Blueprint('inicio', __name__)


@inicio_bp.route('/')
def index():
    return render_template('index.html')

@inicio_bp.errorhandler(401)
def status_401(error):

    if current_user.is_authenticated:
        boton_volver = '/perfil'
    else:
        boton_volver = '/'


    return render_template('error_401.html', boton_volver=boton_volver)

@inicio_bp.errorhandler(404)
def status_404(error):
    if current_user.is_authenticated:
        boton_volver = '/perfil'
    else:
        boton_volver = '/'
    return render_template('error_404.html', boton_volver=boton_volver)