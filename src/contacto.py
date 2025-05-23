from flask import Blueprint, render_template, flash, request
from flask_login import current_user
from forms import Contacto  # Importa tu formulario
from config import Config
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

contacto_bp = Blueprint('contacto', __name__)

@contacto_bp.route('/contacto', methods = ['GET', 'POST'])
def contacto():
    try:
        formulario = Contacto()
        if current_user.is_authenticated:
                nombre = current_user.nombre
                correo = current_user.correo
                volver = '/perfil'
        else:
            nombre = ''
            correo = ''
            volver = '/'
        if formulario.validate_on_submit and request.method == 'POST':
            if current_user.is_authenticated:
                nombre = current_user.nombre
                correo = current_user.correo
                volver = '/perfil'
            else:
                nombre = request.form.get('nombre')
                correo = request.form.get('correo')
                volver = '/'
            
            mensaje_formulario = request.form.get('mensaje')
            #Preparamos las credenciales del correo para poder enviar correos

            servidor_smtp = "smtp.gmail.com"
            puerto_smtp = 587
            usuario_smtp = "infocurriculum360@gmail.com"
            clave_smtp = Config['EMAIL_KEY']

            #Preparamos el mensaje para enviarlo por correo

            msg = MIMEMultipart()
            msg['From'] = usuario_smtp
            msg['To'] = usuario_smtp
            msg['Subject'] = "Mensaje de {}".format(nombre)
            mensaje = "{}\nAqui les dejo mi correo electrónico: {}".format(mensaje_formulario, correo)
            msg.attach(MIMEText(mensaje, "plain")) #Esto introduce el mensaje de la linea superior en el cuerpo del correo
            try:
                with smtplib.SMTP(servidor_smtp, puerto_smtp) as server:
                    server.starttls() #Iniciamos la conexion con seguridad 
                    server.login(usuario_smtp, clave_smtp) #Iniciamos sesion en el correo
                    server.sendmail(usuario_smtp, msg["To"], msg.as_string()) #Enviamos el mensaje de bienvenida al nuevo usuario
                    flash("Correo enviado correctamente")
                    return render_template('contacto.html', formulario = formulario, nombre = nombre, correo = correo, boton_volver = volver)  
                    
            except Exception as e:
                flash("Error al enviar correo: {}".format(e))
                return render_template('contacto.html', formulario = formulario, nombre = nombre, correo = correo, boton_volver = volver) 

        return render_template('contacto.html', formulario = formulario, nombre = nombre, correo = correo, boton_volver = volver)
    except Exception as e:
        flash('Ha ocurrido un error: {}'.format(e))
        return render_template('contacto.html', formulario = formulario, nombre = nombre, correo = correo, boton_volver = volver)
