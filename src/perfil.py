from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import current_user, login_required
from forms import Editar_perfil # Importa tu formulario
from config import Config
from extensions import mysql
import os
from werkzeug.utils import secure_filename


perfil_bp = Blueprint('perfil', __name__)

#Esta es la funcion de la interfaz de perfil
@perfil_bp.route('/perfil')
@login_required
def perfil():
    try:
        cursor = mysql.connection.cursor()
        
        # Consulta todos los currículums asociados al usuario actual
        cursor.execute('SELECT id_curriculum, plantilla FROM curriculums INNER JOIN usuarios ON curriculums.id_usuario = usuarios.id WHERE usuarios.id = %s', (current_user.id,))
        curriculums = cursor.fetchall()
        
        # Se guardan en una lista de diccionarios los datos de cada currículum
        curriculums_usuario = []
        for curriculum in curriculums:
            curriculums_usuario.append({'id_curriculum': curriculum[0], 'plantilla': curriculum[1]})
            print(curriculums_usuario)  # Muestra los currículums en consola (útil para depuración)

        cursor.close()
        # Renderiza la plantilla de perfil, enviando los datos del usuario y sus currículums
        return render_template('perfil.html', usuario=current_user, curriculums_usuario=curriculums_usuario)
    
    except:
        # En caso de error, muestra un mensaje
        flash('Ha ocurrido un error:')
        return render_template('perfil.html', usuario=current_user, curriculums_usuario=curriculums_usuario)


# Extensiones permitidas para archivos de imagen
extensiones_permitidas = {'png', 'jpg', 'jpeg', 'gif'}

# Función que valida si el archivo tiene una extensión permitida
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in extensiones_permitidas


# Ruta para editar el perfil del usuario
@perfil_bp.route('/editar_perfil', methods=['GET', 'POST'])
@login_required  # Solo usuarios autenticados pueden acceder
def editar_perfil():
    try:
        formulario = Editar_perfil()  # Se obtiene el formulario para editar el perfil

        # Si se envía el formulario por POST y pasa la validación...
        if formulario.validate_on_submit and request.method == 'POST':
            id = current_user.id  # ID del usuario actual
            nombre = request.form.get('nombre')  # Nuevo nombre
            apellidos = request.form.get('apellidos')  # Nuevos apellidos

            # Si el usuario es el administrador, no puede cambiar su correo
            if current_user.correo == 'infocurriculum360@gmail.com':
                correo = current_user.correo
            else:
                correo = request.form.get('correo')  # Nuevo correo

            # Se intenta obtener la imagen del formulario
            file = request.files.get('imagen')

            # Si se sube un archivo de imagen válido
            if file and hasattr(file, 'filename'):
                filename = secure_filename(file.filename)  # Se asegura que el nombre del archivo sea seguro
                filepath = os.path.normpath(os.path.join(Config.UPLOAD_FOLDER, filename))  # Ruta segura
                print(filepath)
                print("Ruta donde se intentará guardar el archivo:", os.path.abspath(filepath))
                file.save(filepath)  # Guarda la imagen en el servidor
                
                # Ruta relativa para guardar en la base de datos
                ruta_imagen_bd = '../static/img/{}'.format(filename)

                # Actualiza la información del usuario incluyendo la nueva imagen
                cursor = mysql.connection.cursor()
                cursor.execute('UPDATE usuarios SET nombre = %s, apellidos = %s, correo = %s, imagen = %s WHERE id = %s',
                               (nombre, apellidos, correo, ruta_imagen_bd, id))
                mysql.connection.commit()
                cursor.close()
                flash('Datos actualizados correctamente') # Muestra un mensaje de que todo se ha actualizado bien
                return redirect(url_for('perfil.perfil'))

            # Si no se subió imagen, solo actualiza nombre, apellidos y correo
            cursor = mysql.connection.cursor()
            cursor.execute('UPDATE usuarios SET nombre = %s, apellidos = %s, correo = %s WHERE id = %s',
                           (nombre, apellidos, correo, id))
            mysql.connection.commit()
            cursor.close()
            flash('Datos actualizados correctamente')
            return redirect(url_for('perfil.perfil'))

        return render_template('editar_perfil.html', usuario=current_user, formulario=formulario)

    except:
        flash('Ha ocurrido un error')
        return render_template('editar_perfil.html', usuario=current_user, formulario=formulario)
