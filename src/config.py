import os
from dotenv import load_dotenv

load_dotenv()  # Cargar variables desde .env

#AQUI SE OBTIENEN TODAS LAS VARIABLES DE ENTORNO DEL .env
basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    MYSQL_HOST = os.getenv('MYSQL_HOST') # Host de la BD
    MYSQL_USER = os.getenv('MYSQL_USER') # Usuario en el cliente de la BD
    MYSQL_PASSWORD = os.getenv('MYSQL_PASSWORD') # Clave en el cliente de la BD
    MYSQL_DB = os.getenv('MYSQL_DB') # Nombre de la BD
    EMAIL_KEY = os.getenv('EMAIL_KEY') # Clave del correo para enviar correos electronicos
    SECRET_KEY = os.getenv('SECRET_KEY') #Clave secreta
    UPLOAD_FOLDER = os.getenv('UPLOAD_FOLDER') # Ruta donde se guardan las imagenes que el usuario introduzca para su perfil
