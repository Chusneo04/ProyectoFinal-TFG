from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import current_user
from forms import Recuperar_clave_email, Nueva_Clave  # Importa tu formulario
from config import Config
from extensions import mysql
from werkzeug.security import generate_password_hash
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from secrets import token_urlsafe

recuperar_clave_bp = Blueprint('recuperar_clave', __name__)


@recuperar_clave_bp.route('/recuperar_clave', methods = ['GET', 'POST'])
def recuperar_clave():
    try:
        if current_user.is_authenticated:
            return redirect(url_for('perfil.perfil'))
        
        cursor = mysql.connection.cursor()
        formulario_email = Recuperar_clave_email()

        if formulario_email.validate_on_submit and request.method == 'POST':
            correo = request.form.get('correo')
            cursor.execute('SELECT * FROM usuarios WHERE correo = %s', (correo,))
            usuario_existe = cursor.fetchone()
            print(usuario_existe)
            if not usuario_existe:
                flash('El usuario no existe')
                return render_template('recuperar_contraseña.html', formulario = formulario_email)
            
            else:
                token = token_urlsafe(32)
                print(token)
                cursor = mysql.connection.cursor()
                cursor.execute('UPDATE usuarios SET token = %s WHERE correo = %s', (token, correo))
                mysql.connection.commit()
                reset_url = url_for('nueva_clave', token = token, _external = True)

                #Preparamos las credenciales del correo para poder enviar correos

                servidor_smtp = "smtp.gmail.com"
                puerto_smtp = 587
                usuario_smtp = "infocurriculum360@gmail.com"
                clave_smtp = Config['EMAIL_KEY']

                #Preparamos el mensaje para enviarlo por correo

                msg = MIMEMultipart()
                msg['From'] = usuario_smtp
                msg['To'] = correo
                msg['Subject'] = "Recuperación de contraseña"
                mensaje = "Para recuperar la contraseña accede al siguiente enlace: {}".format(reset_url)
                msg.attach(MIMEText(mensaje, "plain")) #Esto introduce el mensaje de la linea superior en el cuerpo del correo
                try:
                    with smtplib.SMTP(servidor_smtp, puerto_smtp) as server:
                        server.starttls() #Iniciamos la conexion con seguridad 
                        server.login(usuario_smtp, clave_smtp) #Iniciamos sesion en el correo
                        server.sendmail(usuario_smtp, msg["To"], msg.as_string()) #Enviamos el mensaje de bienvenida al nuevo usuario
                        flash("Correo enviado correctamente")
                        return render_template('recuperar_contraseña.html', formulario = formulario_email)  
                     
                except Exception as e:
                    flash("Error al enviar correo: {}".format(e))
                    return render_template('recuperar_contraseña.html', formulario = formulario_email)
    except Exception as e:
        flash('Ha ocurrido un error, {}'.format(e))
        return render_template('recuperar_contraseña.html', formulario = formulario_email)
    return render_template('recuperar_contraseña.html', formulario = formulario_email)


@recuperar_clave_bp.route('/nueva_clave/<token>', methods = ['GET', 'POST'])
def nueva_clave(token):

    try:
        if current_user.is_authenticated:
            return redirect(url_for('perfil.perfil'))
        cursor = mysql.connection.cursor()
        cursor.execute('SELECT * FROM usuarios WHERE token = %s', (token,))
        usuario_existe = cursor.fetchone()

        if not usuario_existe:
            flash('El enlace ha caducado')
            return redirect(url_for('recuperar_clave.recuperar_clave'))
        else:
            formulario = Nueva_Clave()

            if formulario.validate_on_submit and request.method == 'POST':
                clave = request.form.get('contraseña')
                clave_confirmada = request.form.get('confirmar_clave')

                if clave != clave_confirmada:
                    flash('Las contraseñas no coinciden')
                    return render_template('nueva_clave.html', formulario = formulario)

                clave = generate_password_hash(clave)
                cursor.execute('UPDATE usuarios SET clave = %s WHERE token = %s', (clave, token))
                mysql.connection.commit()
                cursor.execute('UPDATE usuarios SET token = %s WHERE token = %s', (None, token))
                mysql.connection.commit()
                return redirect(url_for('auth.login'))
    except Exception as e:
        flash('Ha ocurrido un error')
        return render_template('nueva_clave.html', formulario = formulario)
    return render_template('nueva_clave.html', formulario = formulario)
