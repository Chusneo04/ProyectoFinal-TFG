from flask import Blueprint, render_template, flash, request
from flask_login import current_user
from forms import Contacto  # Importa tu formulario
from config import Config
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

contacto_bp = Blueprint('contacto', __name__)

@contacto_bp.route('/contacto', methods=['GET', 'POST'])
def contacto():
    try:
        formulario = Contacto()  # Obtenemos el formulario de contacto

        # Si el usuario está logueado, cogemos su nombre y correo para autocompletar los campos del formulario
        if current_user.is_authenticated:
            nombre = current_user.nombre
            correo = current_user.correo
            volver = '/perfil'  # En este caso, el botón de volver redirige al perfil
        else:
            nombre = ''  # Si no está logueado, dejamos vacío para que el usuario rellene
            correo = ''
            volver = '/'  # Botón de volver lleva al inicio

        # Si se envía el formulario y es válido
        if formulario.validate_on_submit and request.method == 'POST':

            # Volvemos a comprobar si el usuario está logueado para actualizar variables
            if current_user.is_authenticated:
                nombre = current_user.nombre
                correo = current_user.correo
                volver = '/perfil'
            else:
                # Si no está logueado, cogemos el nombre y correo que ha introducido en el formulario
                nombre = request.form.get('nombre')
                correo = request.form.get('correo')
                volver = '/'

            mensaje_formulario = request.form.get('mensaje')  # Obtenemos el mensaje del formulario

            # Configuramos los datos para enviar el correo
            servidor_smtp = "smtp.gmail.com"
            puerto_smtp = 587
            usuario_smtp = "infocurriculum360@gmail.com"
            clave_smtp = Config.EMAIL_KEY

            # Construimos el correo
            msg = MIMEMultipart()
            msg['From'] = usuario_smtp
            msg['To'] = usuario_smtp
            msg['Subject'] = "Mensaje de {}".format(nombre)
            mensaje = "{}\nAqui les dejo mi correo electrónico: {}".format(mensaje_formulario, correo)
            msg.attach(MIMEText(mensaje, "plain"))  # Añadimos el mensaje al cuerpo del email

            try:
                with smtplib.SMTP(servidor_smtp, puerto_smtp) as server:
                    server.starttls()  # Activamos conexión segura
                    server.login(usuario_smtp, clave_smtp)  # Iniciamos sesión en el servidor SMTP
                    server.sendmail(usuario_smtp, msg["To"], msg.as_string())  # Enviamos el correo
                    flash("Correo enviado correctamente")  # Mensaje de éxito
                    # Volvemos a renderizar la misma página con el formulario y los datos cargados
                    return render_template('contacto.html', formulario=formulario, nombre=nombre, correo=correo, boton_volver=volver)  
                    
            except:
                # Si falla el envío, mostramos error y renderizamos el formulario
                flash("Error al enviar correo")
                return render_template('contacto.html', formulario=formulario, nombre=nombre, correo=correo, boton_volver=volver) 

        # Si no es POST o formulario inválido, mostramos el formulario normalmente
        return render_template('contacto.html', formulario=formulario, nombre=nombre, correo=correo, boton_volver=volver)

    except:
        flash('Ha ocurrido un error')
        return render_template('contacto.html', formulario=formulario, nombre=nombre, correo=correo, boton_volver=volver)
