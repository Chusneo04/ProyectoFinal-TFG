from flask import Flask, redirect, render_template, request, url_for, flash
import os
from flask_mysqldb import MySQL
from datetime import datetime
from dotenv import load_dotenv
from forms import Usuario
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, UserMixin, login_user, login_required, current_user, logout_user
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage

app = Flask(__name__)

load_dotenv()
mysql = MySQL(app)

#Aqui tenemos la "configuracion" de las credenciales que estan en el .env para acceder a la base de datos

app.config['MYSQL_HOST'] = os.getenv('MYSQL_HOST')
app.config['MYSQL_USER'] = os.getenv('MYSQL_USER')
app.config['MYSQL_PASSWORD'] = os.getenv('MYSQL_PASSWORD')
app.config['MYSQL_DB'] = os.getenv('MYSQL_DB')
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')

#Aqui definimos el objeto del usuario para usarlo mas adelante

class User(UserMixin):
    def __init__(self, id, nombre, apellidos, correo, clave, fecha):
        self.id = str(id)
        self.nombre = nombre
        self.apellidos = apellidos
        self.correo = correo
        self.clave = clave
        self.fecha = fecha

login_manager = LoginManager()
login_manager.init_app(app)

#Aqui tenemos la funcion con la que se carga el usuario para poder gestionar la sesión

@login_manager.user_loader
def load_user(id):
    try:
        cursor = mysql.connection.cursor() #Aqui abrimos el cursor de la base de datos
        cursor.execute("SELECT id, nombre, apellidos, correo, clave, fecha_de_creacion FROM usuarios WHERE id = %s", (id,)) #Aqui obtenemos el usuario para comprobar si existe en la base de datos
        user = cursor.fetchone() #Aqui se introducen en una variable los campos que le hemos pedido sobre el usuario en la linea anterior
        cursor.close() #Cerramos el cursor

    #En las 3 siguientes lineas gestionamos una excepcion para que en caso de haber cualquier tipo de error en la busqueda del usuario nos devuelva un mensaje de error
    except Exception as error:
        flash("Error al cargar usuario")
        return None
    
    #Aqui nos devuelve el usuario en caso de que haya salido todo correcto y sin que haya saltado la excepción anterior
    if user:
        return User(user[0], user[1], user[2], user[3], user[4], user[5])
    return None


@app.route('/')
def index():
    return render_template('index.html')


#Esta es la funcion de la interfaz de registro

@app.route('/register', methods = ['GET', 'POST'])
def register():

    try:
        #Aqui comprobamos si el usuario ya esta autenticado, si lo está te redirije a la interfaz de perfil

        if current_user.is_authenticated:
            return redirect(url_for('perfil'))


        cursor = mysql.connection.cursor()
        usuario = Usuario() #Aqui traemos el formulario para llevar a cabo el registro del usuario

        #Si todos los campos del formulario se han validado correctamente 

        if usuario.validate_on_submit and request.method == 'POST':

            #Obtenemos todos los datos sobre el usuario para almacenarlo en la base de datos en caso de que no exista previamente

            nombre = request.form.get('nombre')
            apellidos = request.form.get('apellidos')
            correo = request.form.get('correo')
            clave = request.form.get('clave')
            clave = generate_password_hash(clave)
            fecha = datetime.now()

            cursor.execute('SELECT * FROM usuarios WHERE correo = %s', (correo,)) #Aqui comprobamos si el usuario existe ya en la base de datos
            usuario_existente = cursor.fetchone()

            #Aqui le mostramos un mensaje al usuario en caso de que ya esté registrado anteriormente

            if usuario_existente:
                flash('El usuario ya existe')

            #Aqui llevamos a cabo el registro del nuevo usuario
            else:
                #Introducimos al usuario en la base de datos con los campos correspondientes
                cursor.execute('INSERT INTO usuarios(nombre, apellidos, correo, clave, fecha_de_creacion) VALUES (%s, %s, %s, %s, %s)', (nombre, apellidos, correo, clave, fecha))
                mysql.connection.commit() #Guardamos los cambios

                #Obtenemos el nuevo usuario una vez ya está registrado en la base de datos

                cursor.execute('SELECT id, nombre, apellidos, correo, clave, fecha_de_creacion FROM usuarios WHERE correo = %s', (correo,))
                nuevo_usuario = cursor.fetchone()
                #Y aqui ya llevamos a cabo el inicio de sesión para que pueda acceder a las rutas protegidas
                if nuevo_usuario:
                    usuario_obj = User(nuevo_usuario[0], nuevo_usuario[1], nuevo_usuario[2], nuevo_usuario[3], nuevo_usuario[4], nuevo_usuario[5])
                    print(type(nuevo_usuario[3]))
                    login_user(usuario_obj)

                    #Preparamos las credenciales del correo para poder enviar correos

                    servidor_smtp = "smtp.gmail.com"
                    puerto_smtp = 587
                    usuario_smtp = "infocurriculum360@gmail.com"
                    clave_smtp = os.getenv('EMAIL_KEY')

                    #Preparamos el mensaje para enviarlo por correo

                    msg = MIMEMultipart()
                    msg['From'] = usuario_smtp
                    msg['To'] = nuevo_usuario[3]
                    msg['Subject'] = "Bienvenido {}".format(nuevo_usuario[1])
                    mensaje = "¡Bienvenido/a a Curriculum360! Nos alegra que formes parte de nuestra comunidad.Aquí encontrarás herramientas para mejorar tu perfil profesional, organizar tu experiencia y destacar tu talento. Nos comprometemos a ayudarte en cada paso del camino."
                    msg.attach(MIMEText(mensaje, "plain")) #Esto introduce el mensaje de la linea superior en el cuerpo del correo
                    try:
                        with smtplib.SMTP(servidor_smtp, puerto_smtp) as server:
                            server.starttls() #Iniciamos la conexion con seguridad 
                            server.login(usuario_smtp, clave_smtp) #Iniciamos sesion en el correo
                            server.sendmail(usuario_smtp, msg["To"], msg.as_string()) #Enviamos el mensaje de bienvenida al nuevo usuario
                            print("Correo enviado correctamente")
                            return redirect(url_for('perfil')) #Si todo va bien redirigirá al usuario a la interfaz de perfil
                    except Exception as e:
                        print('144')
                        print("Error al enviar correo: {}".format(e))
                        return render_template('register.html', usuario=usuario)


                    
                return render_template('register.html', usuario=usuario) #Si algo falla te vuelve a mostrar la de registro

        return render_template('register.html', usuario=usuario) #Muestra la interfaz de registro y envia al html el formulario para gestionar alli el diseño   

    except:
        flash('Error al registrar')
        return render_template('register.html', usuario=usuario)

    
#Esta es la funcion de la interfaz de perfil

@app.route('/perfil')
@login_required #Esta linea significa que para poder acceder a esta interfaz debes tener la sesion iniciada, si no es asi no permitira el acceso
def perfil():
    return render_template('perfil.html')

#Esta es la funcion que cierra la sesión para que el usuario pueda acceder a las rutas en las que no puedes tener una sesion iniciada

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)