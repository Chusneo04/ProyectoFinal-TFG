from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import current_user, login_required
from werkzeug.security import check_password_hash
from forms import Editar_clave, Clave_nueva  # Importa tu formulario
from extensions import mysql
from werkzeug.security import generate_password_hash, check_password_hash

editar_clave_perfil_bp = Blueprint('editar_clave_perfil', __name__)

@editar_clave_perfil_bp.route('/editar_clave', methods = ['GET', 'POST'])
@login_required
def editar_clave():
    try:
        formulario = Editar_clave()
        if formulario.validate_on_submit and request.method == 'POST':
            id = current_user.id
            cursor = mysql.connection.cursor()
            cursor.execute('SELECT clave FROM usuarios WHERE id = %s', (id,))
            clave_almacenada = cursor.fetchone()
            clave_introducida = request.form.get('contraseña')
            if check_password_hash(clave_almacenada[0], clave_introducida):
                return redirect(url_for('editar_clave_perfil.clave_nueva'))
            flash('La contraseña introducida no es correcta')
        return render_template('editar_clave.html', formulario = formulario, usuario = current_user)
    except Exception as e:
        flash('Ha ocurrrido un error: {}'.format(e))
        return render_template('editar_clave.html', formulario = formulario, usuario = current_user)

@editar_clave_perfil_bp.route('/clave_nueva', methods = ['GET', 'POST'])
@login_required
def clave_nueva():

    try:
        formulario = Clave_nueva()

        if formulario.validate_on_submit and request.method == 'POST':
            id = current_user.id
            clave = request.form.get('contraseña')
            clave = generate_password_hash(clave)
            cursor = mysql.connection.cursor()
            cursor.execute('UPDATE usuarios SET clave = %s WHERE id = %s', (clave, id))
            mysql.connection.commit()
            flash('Clave actualizada correctamente')
            return redirect(url_for('perfil.perfil'))
    except Exception as e:
        flash('Ha ocurrido un error')
        return render_template('clave_nueva.html', formulario = formulario)
    return render_template('clave_nueva.html', formulario = formulario)
