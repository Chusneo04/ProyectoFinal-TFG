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

@recuperar_clave_bp.route('/recuperar_clave', methods=['GET', 'POST'])
def recuperar_clave():
    try:
        # Si el usuario ya está logueado, le mandamos al perfil directamente
        if current_user.is_authenticated:
            return redirect(url_for('perfil.perfil'))
        
        cursor = mysql.connection.cursor()
        formulario_email = Recuperar_clave_email()  # Obtenemos el formulario para pedir el email

        # Si el formulario es válido y se ha enviado
        if formulario_email.validate_on_submit and request.method == 'POST':
            correo = request.form.get('correo')  # Cogemos el email que ha puesto el usuario y buscamos el usuario por ese email
            cursor.execute('SELECT * FROM usuarios WHERE correo = %s', (correo,))
            usuario_existe = cursor.fetchone()

            # Si no existe ningún usuario con ese correo, mostramos mensaje
            if not usuario_existe:
                flash('El usuario no existe')
                return render_template('recuperar_contraseña.html', formulario=formulario_email)
            
            else:
                # Si existe, generamos un token seguro para recuperación
                token = token_urlsafe(32)
                cursor = mysql.connection.cursor()
                cursor.execute('UPDATE usuarios SET token = %s WHERE correo = %s', (token, correo)) # Guardamos el token en la base de datos
                mysql.connection.commit()

                # Creamos la URL completa para que el usuario pueda resetear la contraseña
                reset_url = url_for('recuperar_clave.nueva_clave', token=token, _external=True)

                # Configuramos los datos para enviar el correo
                servidor_smtp = "smtp.gmail.com"
                puerto_smtp = 587
                usuario_smtp = "infocurriculum360@gmail.com"
                clave_smtp = Config.EMAIL_KEY

                # Montamos el correo
                msg = MIMEMultipart()
                msg['From'] = usuario_smtp
                msg['To'] = correo
                msg['Subject'] = "Recuperación de contraseña"
                mensaje = "Para recuperar la contraseña accede al siguiente enlace: {}".format(reset_url)
                msg.attach(MIMEText(mensaje, "plain"))

                try:
                    with smtplib.SMTP(servidor_smtp, puerto_smtp) as server:
                        server.starttls()  # Activamos la conexión segura
                        server.login(usuario_smtp, clave_smtp)  # Iniciamos sesión en el servidor SMTP
                        server.sendmail(usuario_smtp, msg["To"], msg.as_string())  # Enviamos el email
                        flash("Correo enviado correctamente")
                        return render_template('recuperar_contraseña.html', formulario=formulario_email)
                     
                except:
                    # Si falla algo mostramos un mensaje
                    flash("Error al enviar correo")
                    return render_template('recuperar_contraseña.html', formulario=formulario_email)

    except:
        # Si algo falla en todo el proceso, mostramos mensaje
        flash('Ha ocurrido un error')
        return render_template('recuperar_contraseña.html', formulario=formulario_email)

    # Por defecto, renderizamos la página con el formulario vacío
    return render_template('recuperar_contraseña.html', formulario=formulario_email)


@recuperar_clave_bp.route('/nueva_clave/<token>', methods=['GET', 'POST']) # Pasamos el token para que sepa quien es el que tiene que cambiar la clave
def nueva_clave(token):
    try:
        # Si el usuario ya está logueado, lo mandamos al perfil
        if current_user.is_authenticated:
            return redirect(url_for('perfil.perfil'))

        cursor = mysql.connection.cursor()
        # Buscamos un usuario con el token recibido en la URL
        cursor.execute('SELECT * FROM usuarios WHERE token = %s', (token,))
        usuario_existe = cursor.fetchone()

        # Si no hay usuario con ese token el enlace ya no vale y mostramos mensaje por pantalla
        if not usuario_existe:
            flash('El enlace ha caducado')
            return redirect(url_for('recuperar_clave.recuperar_clave'))
        else:
            formulario = Nueva_Clave()  # Obtenemos el formulario para la nueva contraseña

            # Si el formulario se envía y es válido
            if formulario.validate_on_submit and request.method == 'POST':
                clave = request.form.get('contraseña')
                clave_confirmada = request.form.get('confirmar_clave')

                # Comprobamos que ambas contraseñas coincidan
                if clave != clave_confirmada:
                    flash('Las contraseñas no coinciden')
                    return render_template('nueva_clave.html', formulario=formulario)

                # Hasheamos la nueva contraseña y la actualizamos en la base de datos
                clave = generate_password_hash(clave)
                cursor.execute('UPDATE usuarios SET clave = %s WHERE token = %s', (clave, token))
                mysql.connection.commit()

                # Limpiamos el token para que no se pueda reutilizar, esto hace que solo sea de un uso
                cursor.execute('UPDATE usuarios SET token = %s WHERE token = %s', (None, token))
                mysql.connection.commit()

                # Redirigimos al login para que inicie sesión con la nueva contraseña
                return redirect(url_for('auth.login'))

    except:
        # Si algo falla mostramos mensaje genérico y el formulario
        flash('Ha ocurrido un error')
        return render_template('nueva_clave.html', formulario=formulario)

    # Renderizamos la plantilla con el formulario para que el usuario pueda meter la nueva clave
    return render_template('nueva_clave.html', formulario=formulario)
