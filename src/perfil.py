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


# Ruta para editar el perfil del usuario
@perfil_bp.route('/editar_perfil', methods=['GET', 'POST'])
@login_required  # Solo usuarios autenticados pueden acceder
def editar_perfil():
    try:
        formulario = Editar_perfil()  # Se obtiene el formulario para editar el perfil
        
        # Si se envía el formulario por POST y pasa la validación...
        if formulario.validate_on_submit and request.method == 'POST':
            id = current_user.id  # ID del usuario actual
            nombre = request.form.get('nombre').strip()  # Nuevo nombre
            apellidos = request.form.get('apellidos').strip()  # Nuevos apellidos
            

            # Si el usuario es el administrador, no puede cambiar su correo
            if current_user.correo == 'infocurriculum360@gmail.com':
                correo = current_user.correo
            else:
                correo = request.form.get('correo')  # Nuevo correo
            # Validamos que nombre y apellidos solo tengan letras y si hay espacios que esten en el interior y no al principio y final y que la clave no tenga espacios
            cursor = mysql.connection.cursor()
            cursor.execute('SELECT * FROM usuarios WHERE correo = %s', (correo,))
            usuario_existente = cursor.fetchone()
            #Comprobamos que el correo no es el del usuario actual, en ese caso declaramos que usuario_existente es false para que no entre en el condicional de los mensajes de error
            if correo == current_user.correo:
                usuario_existente = False
            
            if not nombre.replace(' ', '').isalpha() or not apellidos.replace(' ', '').isalpha() or usuario_existente:
                
                #Aqui abajo depende lo que falle muestra el error o errores que corresponda por pantalla
                if not nombre.replace(' ', '').isalpha():
                    flash('El nombre debe contener solo letras')
                if not apellidos.replace(' ', '').isalpha():
                    flash('Los apellidos deben ser solo letras')
                if usuario_existente:
                    flash('El correo ya esta en uso')
                return render_template('editar_perfil.html', formulario=formulario) # Muestra la interfaz de editar perfil con los mensajes correspondientes por pantalla

            
            # Se intenta obtener la imagen del formulario
            file = request.files.get('imagen')

            # Si se sube un archivo de imagen válido
            if file and hasattr(file, 'filename'):
                filename = secure_filename(file.filename)  # Se asegura que el nombre del archivo sea seguro
                
                filepath = os.path.normpath(os.path.join(Config.UPLOAD_FOLDER, filename))  # Ruta segura
                
                extension = '.' in filename and filename.rsplit('.', 1)[1].lower() #Obtenemos la extensión del archivo introducido
                extensiones_permitidas = ['png', 'jpg', 'jpeg', 'gif'] #Estas son las extensiones que permitiremos introducir 
                if extension not in extensiones_permitidas: #Comprobamos si la extensión del fichero es una de las permitidas, en caso contrario mostrara un mensaje por pantalla de que no puede introducir ese archivo y con los que tiene que probar.
                    flash('La extensión de la imagen introducida no está permitida. Pruebe con .jpg, .jpeg, .png o .gif')
                    return render_template('editar_perfil.html', usuario=current_user, formulario=formulario)
                print(filename)
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
