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
@login_required #Esta linea significa que para poder acceder a esta interfaz debes tener la sesion iniciada, si no es asi no permitira el acceso
def perfil():
    try:
        cursor = mysql.connection.cursor()
        cursor.execute('SELECT id_curriculum, plantilla FROM curriculums INNER JOIN usuarios ON curriculums.id_usuario = usuarios.id WHERE usuarios.id = %s', (current_user.id,))
        curriculums = cursor.fetchall()
        curriculums_usuario = []
        for curriculum in curriculums:
            curriculums_usuario.append({'id_curriculum': curriculum[0], 'plantilla':curriculum[1]})
            print(curriculums_usuario)
        return render_template('perfil.html', usuario = current_user, curriculums_usuario = curriculums_usuario)
    except Exception as e:
        flash('Ha ocurrido un errror: {}'.format(e))
        return render_template('perfil.html', usuario = current_user, curriculums_usuario = curriculums_usuario)





extensiones_permitidas = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in extensiones_permitidas


#Esta es la funcion que cierra la sesión para que el usuario pueda acceder a las rutas en las que no puedes tener una sesion iniciada

@perfil_bp.route('/editar_perfil', methods = ['GET', 'POST'])
@login_required
def editar_perfil():
    try:
        formulario = Editar_perfil()

        if formulario.validate_on_submit and request.method == 'POST':
            id = current_user.id
            nombre = request.form.get('nombre')
            apellidos = request.form.get('apellidos')
            correo = request.form.get('correo')

            file = request.files.get('imagen')
            print(file)
            if file and hasattr(file, 'filename'):
                filename = secure_filename(file.filename)
                filepath = os.path.normpath(os.path.join(Config['UPLOAD_FOLDER'], filename))
                print(filepath)
                print("Ruta donde se intentará guardar el archivo:", os.path.abspath(filepath))
                file.save(filepath)
                ruta_imagen_bd = '../static/img/{}'.format(filename)
                print(ruta_imagen_bd)
            cursor = mysql.connection.cursor()
            cursor.execute('UPDATE usuarios SET nombre = %s, apellidos = %s, correo = %s, imagen = %s WHERE id = %s', (nombre, apellidos, correo, ruta_imagen_bd, id))
            mysql.connection.commit()
            flash('Datos actualizados correctamente')
            return redirect(url_for('perfil.perfil'))

        return render_template('editar_perfil.html', usuario = current_user, formulario = formulario)
    except Exception as e:
        flash('Ha ocurrido un error: {}'.format(e))
        return render_template('editar_perfil.html', usuario = current_user, formulario = formulario)
