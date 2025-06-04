from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import current_user, login_required
from werkzeug.security import check_password_hash
from forms import Editar_clave, Clave_nueva  # Importa tu formulario
from extensions import mysql
from werkzeug.security import generate_password_hash, check_password_hash

editar_clave_perfil_bp = Blueprint('editar_clave_perfil', __name__)

# Definimos la ruta para editar la contraseña del perfil, permitiendo métodos GET y POST
@editar_clave_perfil_bp.route('/editar_clave', methods = ['GET', 'POST'])
@login_required  # Nos aseguramos de que el usuario esté autenticado para acceder
def editar_clave():
    try:
        formulario = Editar_clave()# Obtenemos el formulario de edición de contraseña

        # Comprobamos si el formulario ha sido enviado y es válido
        if formulario.validate_on_submit and request.method == 'POST':
            id = current_user.id 
            cursor = mysql.connection.cursor()
            # Consultamos la contraseña almacenada en la base de datos
            cursor.execute('SELECT clave FROM usuarios WHERE id = %s', (id,))
            clave_almacenada = cursor.fetchone()

            # Obtenemos la contraseña introducida por el usuario
            clave_introducida = request.form.get('contraseña')

            # Verificamos si la contraseña introducida coincide con la almacenada
            if check_password_hash(clave_almacenada[0], clave_introducida):
                # Si es correcta, redirigimos a la vista para introducir la nueva contraseña
                return redirect(url_for('editar_clave_perfil.clave_nueva'))
            # Mostramos un mensaje por pantalla si la contraseña no coincide
            flash('La contraseña introducida no es correcta')
        # Renderizamos la plantilla del formulario
        return render_template('editar_clave.html', formulario = formulario, usuario = current_user)
    except Exception as e:
        # Mostramos un mensaje de error si algo falla
        flash('Ha ocurrrido un error: {}'.format(e))
        return render_template('editar_clave.html', formulario = formulario, usuario = current_user)

# Definimos la ruta para introducir una nueva contraseña
@editar_clave_perfil_bp.route('/clave_nueva', methods = ['GET', 'POST'])
@login_required  # Solo usuarios autenticados pueden acceder
def clave_nueva():

    try:
        # Obtenemos el formulario para la nueva contraseña
        formulario = Clave_nueva()

        # Comprobamos si el formulario ha sido enviado y es válido
        if formulario.validate_on_submit and request.method == 'POST':
            id = current_user.id  # Obtenemos el ID del usuario actual
            clave = request.form.get('contraseña')  # Obtenemos la nueva contraseña introducida por el usuario
            clave = generate_password_hash(clave)  # Encriptamos la nueva contraseña para guardarla con mayor seguridad
            cursor = mysql.connection.cursor()

            # Actualizamos la contraseña en la base de datos
            cursor.execute('UPDATE usuarios SET clave = %s WHERE id = %s', (clave, id))
            mysql.connection.commit()

            # Mostramos un mensaje de confirmación por pantalla y redirigimos al perfil
            flash('Clave actualizada correctamente')
            return redirect(url_for('perfil.perfil'))
    except Exception as e:
        # Mostramos un mensaje de error si algo falla
        flash('Ha ocurrido un error')
        return render_template('clave_nueva.html', formulario = formulario)
    # Renderizamos el formulario por defecto si no se ha enviado
    return render_template('clave_nueva.html', formulario = formulario)
