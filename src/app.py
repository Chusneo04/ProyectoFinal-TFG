from flask import Flask, render_template
from flask_login import current_user
from config import Config
from extensions import mysql, login_manager
from auth import auth_bp
from recuperar_clave import recuperar_clave_bp
from perfil import perfil_bp
from editar_clave_perfil import editar_clave_perfil_bp
from contacto import contacto_bp
from crear_curriculum import crear_curriculum_bp
from modificar_curriculum import modificar_curriculum_bp
from inicio import inicio_bp
from admin import admin_bp


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)  # Le pasamos config 

    # Aqui inicializamos las extensiones que vamos a usar (base de datos y login)
    mysql.init_app(app)
    login_manager.init_app(app)

    # Manejamos el error 401 cuando alguien no tiene permisos para acceder a alguna ruta
    @app.errorhandler(401)
    def status_401(error):
        # Si el usuario esta autenticado el boton volver redirige a perfil, si no redirige a raiz
        if current_user.is_authenticated:
            boton_volver = '/perfil'
        else:
            boton_volver = '/'
        return render_template('error_401.html', boton_volver=boton_volver)

    # Manejamos el error 404 (cuando no encuentra una página)
    @app.errorhandler(404)
    def status_404(error):
        # Mismo criterio que el 401, si esta logueado, va al perfil; si no, al inicio
        if current_user.is_authenticated:
            boton_volver = '/perfil'
        else:
            boton_volver = '/'
        return render_template('error_404.html', boton_volver=boton_volver)

    # Registramos todos los blueprints que usamos en la aplicacion

    # Todos funcionan a partir de la ruta raiz, por eso tienen el mismo url_prefix
    app.register_blueprint(inicio_bp, url_prefix="/")                  # Página principal
    app.register_blueprint(auth_bp, url_prefix="/")                    # Rutas de autenticación (Login y Register)
    app.register_blueprint(recuperar_clave_bp, url_prefix="/")        # Rutas de recuperar contraseña
    app.register_blueprint(perfil_bp, url_prefix="/")                  # Rutas del perfil de usuario
    app.register_blueprint(editar_clave_perfil_bp, url_prefix="/")    # Cambiar contraseña desde editar perfil
    app.register_blueprint(contacto_bp, url_prefix="/")                # Formulario de contacto
    app.register_blueprint(crear_curriculum_bp, url_prefix="/")       # Crear nuevo CV
    app.register_blueprint(modificar_curriculum_bp, url_prefix="/")   # Modificar y eliminar curriculums
    app.register_blueprint(admin_bp, url_prefix="/")                   # Rutas del admin

    return app  # Devolvemos la app ya configurada para poder usarla



