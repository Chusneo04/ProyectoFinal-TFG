from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, current_user, login_required
from werkzeug.security import check_password_hash
from models import User  # Asegúrate de importar tu modelo de usuario
from forms import Usuario_login, Usuario_register  # Importa tu formulario
from config import Config
from extensions import mysql, login_manager
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from flask import Blueprint, flash


auth_bp = Blueprint('auth', __name__)


#Aqui tenemos la funcion con la que se carga el usuario para poder gestionar la sesión
@login_manager.user_loader
def load_user(id):
    try:
        cursor = mysql.connection.cursor() #Aqui abrimos el cursor de la base de datos
        cursor.execute("SELECT id, nombre, apellidos, correo, clave, fecha_de_creacion, token FROM usuarios WHERE id = %s", (id,)) #Aqui obtenemos el usuario para comprobar si existe en la base de datos
        user = cursor.fetchone() #Aqui se introducen en una variable los campos que le hemos pedido sobre el usuario en la linea anterior
        cursor.close() #Cerramos el cursor

    #En las 3 siguientes lineas gestionamos una excepcion para que en caso de haber cualquier tipo de error en la busqueda del usuario nos devuelva un mensaje de error
    except Exception as error:
        flash("Error al cargar usuario")
        return None
    
    #Aqui nos devuelve el usuario en caso de que haya salido todo correcto y sin que haya saltado la excepción anterior
    if user:
        return User(user[0], user[1], user[2], user[3], user[4], user[5], user[6])
    return None


#Esta es la funcion de la interfaz de registro

@auth_bp.route('/register', methods = ['GET', 'POST'])
def register():

    try:
        #Aqui comprobamos si el usuario ya esta autenticado, si lo está te redirije a la interfaz de perfil

        if current_user.is_authenticated:
            return redirect(url_for('perfil.perfil'))


        cursor = mysql.connection.cursor()
        usuario = Usuario_register() #Aqui traemos el formulario para llevar a cabo el registro del usuario

        #Si todos los campos del formulario se han validado correctamente 

        if usuario.validate_on_submit and request.method == 'POST':

            #Obtenemos todos los datos sobre el usuario para almacenarlo en la base de datos en caso de que no exista previamente

            nombre = request.form.get('nombre')
            apellidos = request.form.get('apellidos')
            correo = request.form.get('correo')
            clave = request.form.get('clave')
            clave = generate_password_hash(clave)
            fecha = datetime.now()
            token = None

            cursor.execute('SELECT * FROM usuarios WHERE correo = %s', (correo,)) #Aqui comprobamos si el usuario existe ya en la base de datos
            usuario_existente = cursor.fetchone()

            #Aqui le mostramos un mensaje al usuario en caso de que ya esté registrado anteriormente

            if usuario_existente:
                flash('El usuario ya existe')

            #Aqui llevamos a cabo el registro del nuevo usuario
            else:
                #Introducimos al usuario en la base de datos con los campos correspondientes
                cursor.execute('INSERT INTO usuarios(nombre, apellidos, correo, clave, fecha_de_creacion, token, imagen) VALUES (%s, %s, %s, %s, %s, %s, %s)', (nombre, apellidos, correo, clave, fecha, token, '../static/img/user.png'))
                mysql.connection.commit() #Guardamos los cambios
                print('110')
                #Obtenemos el nuevo usuario una vez ya está registrado en la base de datos

                cursor.execute('SELECT id, nombre, apellidos, correo, clave, fecha_de_creacion, token FROM usuarios WHERE correo = %s', (correo,))
                nuevo_usuario = cursor.fetchone()
                print('111')
                #Y aqui ya llevamos a cabo el inicio de sesión para que pueda acceder a las rutas protegidas
                if nuevo_usuario:
                    print('Hola')
                    usuario_obj = User(nuevo_usuario[0], nuevo_usuario[1], nuevo_usuario[2], nuevo_usuario[3], nuevo_usuario[4], nuevo_usuario[5], nuevo_usuario[6])
                    print('Adios')
                    print(type(nuevo_usuario[3]))
                    login_user(usuario_obj)
                    print('112')
                    #Preparamos las credenciales del correo para poder enviar correos

                    servidor_smtp = "smtp.gmail.com"
                    puerto_smtp = 587
                    usuario_smtp = "infocurriculum360@gmail.com"
                    clave_smtp = Config['EMAIL_KEY']


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
                            return redirect(url_for('perfil.perfil')) #Si todo va bien redirigirá al usuario a la interfaz de perfil
                    except Exception as e:
                        print("Error al enviar correo: {}".format(e))
                        return render_template('register.html', usuario=usuario)



                return render_template('register.html', usuario=usuario) #Si algo falla te vuelve a mostrar la de registro

        return render_template('register.html', usuario=usuario) #Muestra la interfaz de registro y envia al html el formulario para gestionar alli el diseño   

    except:
        flash('Error al registrar')
        return render_template('register.html', usuario=usuario)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    try:
        #Aqui comprobamos si el usuario ya esta autenticado, si lo está te redirije a la interfaz de perfil

        if current_user.is_authenticated:
            return redirect(url_for('perfil.perfil'))


        cursor = mysql.connection.cursor()
        usuario = Usuario_login() #Aqui traemos el formulario para llevar a cabo el registro del usuario

        #Si todos los campos del formulario se han validado correctamente 

        if usuario.validate_on_submit and request.method == 'POST':

            #Obtenemos todos los datos sobre el usuario para proceder al inicio de sesión

            correo = request.form.get('correo')
            clave = request.form.get('clave')

            cursor.execute('SELECT * FROM usuarios WHERE correo = %s', (correo,)) #Aqui comprobamos si el usuario existe ya en la base de datos
            usuario_existente = cursor.fetchone()

            #Aqui le mostramos un mensaje al usuario en caso de que no esté registrado

            if not usuario_existente:
                flash('Las credenciales introducidas son incorrectas')
                return render_template('login.html', usuario=usuario)

            else:
                #Y aqui ya llevamos a cabo el inicio de sesión para que pueda acceder a las rutas protegidas
                print('192')
                if check_password_hash(usuario_existente[4], clave):
                    print('194')
                    usuario_obj = User(usuario_existente[0], usuario_existente[1], usuario_existente[2], usuario_existente[3], usuario_existente[4], usuario_existente[5], usuario_existente[6])
                    print('196')
                    login_user(usuario_obj)
                    print('198')
                    return redirect(url_for('perfil.perfil')) #Si todo va bien redirige al usuario a la interfaz de perfil 
                else:
                    flash('Las credenciales introducidas son incorrectas')
                    return render_template('login.html', usuario=usuario)
        return render_template('login.html', usuario=usuario) #Muestra la interfaz de login y envia al html el formulario para gestionar alli el diseño   

    except:
        flash('Error al Iniciar sesión')
        return render_template('login.html', usuario=usuario)



@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index.index'))