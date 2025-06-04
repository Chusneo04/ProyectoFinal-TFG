from flask import Blueprint, render_template, request, redirect, url_for
from flask_login import current_user

inicio_bp = Blueprint('inicio', __name__)

# Renderizamos la plantilla index si no está autenticado, si lo está redirige a perfil
@inicio_bp.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('perfil.perfil'))
    return render_template('index.html')

