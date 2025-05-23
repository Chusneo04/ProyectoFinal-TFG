from flask import Flask
from config import Config
from extensions import mysql, login_manager
from auth import auth_bp
from recuperar_clave import recuperar_clave_bp
from perfil import perfil_bp
from editar_clave_perfil import editar_clave_perfil_bp
from contacto import contacto_bp
from crear_curriculum import crear_curriculum_bp
from modificar_curriculum import modificar_curriculum_bp
from admin import admin_bp

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Inicializar extensiones
    mysql.init_app(app)
    login_manager.init_app(app)

    # Registrar Blueprints con prefijos claros
    app.register_blueprint(auth_bp, url_prefix="/")
    app.register_blueprint(recuperar_clave_bp, url_prefix="/")
    app.register_blueprint(perfil_bp, url_prefix="/")
    app.register_blueprint(editar_clave_perfil_bp, url_prefix="/")
    app.register_blueprint(contacto_bp, url_prefix="/")
    app.register_blueprint(crear_curriculum_bp, url_prefix="/")
    app.register_blueprint(modificar_curriculum_bp, url_prefix="/")
    app.register_blueprint(admin_bp, url_prefix="/")

    return app