from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, current_user, login_required
from werkzeug.security import check_password_hash, generate_password_hash
from models import User
from forms import Usuario_login, Usuario_register  
from config import Config
from extensions import mysql, login_manager
from datetime import datetime
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


auth_bp = Blueprint('auth', __name__)  # Creamos el blueprint


# Funcion que carga el usuario para gestionar la sesión con Flask-Login
@login_manager.user_loader
def load_user(id):
    try:
        cursor = mysql.connection.cursor()  # Abrimos cursor para la base de datos
        # Consultamos al usuario por su id
        cursor.execute("SELECT id, nombre, apellidos, correo, clave, fecha_de_creacion, token FROM usuarios WHERE id = %s", (id,))
        user = cursor.fetchone()  # Guardamos el resultado
        cursor.close()  # Cerramos el cursor

    except Exception as error:
        flash("Error al cargar usuario")  # Mostramos mensaje de error por pantalla si falla algo
        return None
    
    # Si se encuentra el usuario, devolvemos un objeto User con todos sus datos
    if user:
        return User(user[0], user[1], user[2], user[3], user[4], user[5], user[6])
    return None


# Creamos la ruta register
@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    try:
        # Si ya estamos autenticados nos manda directo al perfil
        if current_user.is_authenticated:
            return redirect(url_for('perfil.perfil'))

        cursor = mysql.connection.cursor()
        usuario = Usuario_register()  # Obtenemos el formulario del registrro

        # Comprobamos que el formulario se haya enviado y sea válido
        if usuario.validate_on_submit and request.method == 'POST':

            # Obtenemos los datos del formulario 
            nombre = request.form.get('nombre').strip() # El strip quita los posibles espacios que puedan haber al princcipio y final
            apellidos = request.form.get('apellidos').strip() # El strip quita los posibles espacios que puedan haber al principio y final
            correo = request.form.get('correo')
            clave = request.form.get('clave')

            # Validamos que nombre y apellidos solo tengan letras y si hay espacios que esten en el interior y no al principio y final y que la clave no tenga espacios
            if not nombre.replace(' ', '').isalpha() or not apellidos.replace(' ', '').isalpha() or ' ' in clave:
                
                #Aqui abajo depende lo que falle muestra el error o errores que corresponda por pantalla
                if not nombre.replace(' ', '').isalpha():
                    flash('El nombre debe contener solo letras')
                if not apellidos.replace(' ', '').isalpha():
                    flash('Los apellidos deben ser solo letras')
                if ' ' in clave:
                    flash('No deben haber espacios en la clave')

                return render_template('register.html', usuario=usuario) # Muestra la interfaz de registro con los mensajes correspondientes por pantalla
            
            # Encriptamos la clave para guardarla en la base de datos de manera segura
            clave = generate_password_hash(clave)
            fecha = datetime.now() # La fecha de creación del usuario
            token = None # Y token que no tiene ningun valor por ahora

            # Comprobamos si el correo ya existe en la base de datos
            cursor.execute('SELECT * FROM usuarios WHERE correo = %s', (correo,))
            usuario_existente = cursor.fetchone()

            if usuario_existente:
                flash('El usuario ya existe') # Si el usuario existe muestra un mensaje por pantalla
            else:
                # Guardamos el usuario en la base de datos
                cursor.execute(
                    'INSERT INTO usuarios(nombre, apellidos, correo, clave, fecha_de_creacion, token, imagen) VALUES (%s, %s, %s, %s, %s, %s, %s)', 
                    (nombre, apellidos, correo, clave, fecha, token, '../static/img/user.png')
                )
                mysql.connection.commit()  # Guardamos los cambios

                # Recuperamos al usuario recién registrado para hacer login automático
                cursor.execute('SELECT id, nombre, apellidos, correo, clave, fecha_de_creacion, token FROM usuarios WHERE correo = %s', (correo,))
                nuevo_usuario = cursor.fetchone()
                cursor.close()
                if nuevo_usuario:
                    usuario_obj = User(nuevo_usuario[0], nuevo_usuario[1], nuevo_usuario[2], nuevo_usuario[3], nuevo_usuario[4], nuevo_usuario[5], nuevo_usuario[6])
                    login_user(usuario_obj)  # Iniciamos sesión automáticamente

                    # Configuramos los datos para enviar el correo de bienvenida
                    servidor_smtp = "smtp.gmail.com"
                    puerto_smtp = 587
                    usuario_smtp = "infocurriculum360@gmail.com"
                    clave_smtp = Config.EMAIL_KEY #Obtiene la clave para poder iniciar sesion

                    # Construimos el mensaje del correo
                    msg = MIMEMultipart()
                    msg['From'] = usuario_smtp #Correo remitente
                    msg['To'] = nuevo_usuario[3] #Correo destinatario
                    msg['Subject'] = "Bienvenido {}".format(nuevo_usuario[1]) #Asunto
                    mensaje = ("¡Bienvenido/a a Curriculum360!\n\n"
                               "Nos alegra que formes parte de nuestra comunidad. "
                               "Aquí encontrarás herramientas para mejorar tu perfil profesional, "
                               "organizar tu experiencia y destacar tu talento. "
                               "Nos comprometemos a ayudarte en cada paso del camino.") #Mensaje de bienvenida
                    msg.attach(MIMEText(mensaje, "plain")) #Se introduce el propio mensaje de bienvenida en el conjunto del mensaje que hay que enviar

                    try:
                        with smtplib.SMTP(servidor_smtp, puerto_smtp) as server:
                            server.starttls()  # Iniciamos conexión segura
                            server.login(usuario_smtp, clave_smtp)  # Login en el servidor SMTP
                            server.sendmail(usuario_smtp, msg["To"], msg.as_string())  # Enviamos el correo
                            print("Correo enviado correctamente")
                            return redirect(url_for('perfil.perfil'))  # Redirigimos al perfil
                    except:
                        print("Error al enviar correo")
                        return render_template('register.html', usuario=usuario)

                return render_template('register.html', usuario=usuario)  # Si falla, volvemos a mostrar registro

        # Si no es POST o no es válido, mostramos el formulario vacío
        return render_template('register.html', usuario=usuario)

    except:
        flash('Error al registrar')
        return render_template('register.html', usuario=usuario)


# Ruta para iniciar sesión
@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    try:
        # Si ya estamos logueados, nos manda directo al perfil
        if current_user.is_authenticated:
            return redirect(url_for('perfil.perfil'))

        cursor = mysql.connection.cursor()
        usuario = Usuario_login()  # Obtenemos el formulario de login

        # Comprobamos que el formulario sea válido y se haya enviado por POST
        if usuario.validate_on_submit and request.method == 'POST':

            correo = request.form.get('correo')
            clave = request.form.get('clave')

            # Buscamos al usuario en la base de datos por correo
            cursor.execute('SELECT * FROM usuarios WHERE correo = %s', (correo,))
            usuario_existente = cursor.fetchone()
            cursor.close()
            if not usuario_existente:
                flash('Las credenciales introducidas son incorrectas')
                return render_template('login.html', usuario=usuario)
            else:
                # Verificamos la contraseña usando el hash guardado
                if check_password_hash(usuario_existente[4], clave):
                    usuario_obj = User(usuario_existente[0], usuario_existente[1], usuario_existente[2], usuario_existente[3], usuario_existente[4], usuario_existente[5], usuario_existente[6])
                    login_user(usuario_obj)  # Iniciamos sesión
                    return redirect(url_for('perfil.perfil'))  # Redirigimos al perfil
                else:
                    flash('Las credenciales introducidas son incorrectas')
                    return render_template('login.html', usuario=usuario)

        # Si no es POST o formulario inválido, mostramos la página de login
        return render_template('login.html', usuario=usuario)

    except:
        flash('Error al iniciar sesión')
        return render_template('login.html', usuario=usuario)


# Ruta para cerrar sesión, solo accesible si estás logueado
@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()  # Cerramos la sesión del usuario
    return redirect(url_for('inicio.index'))  # Redirigimos al inicio
