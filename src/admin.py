from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from extensions import mysql
from models import User  # Importa el modelo de usuario

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/admin')
@login_required
def admin():
    try:
        if current_user.correo != 'infocurriculum360@gmail.com':
            return redirect(url_for('perfil.perfil'))
        
        cursor = mysql.connection.cursor()
        cursor.execute('SELECT id, nombre, apellidos FROM usuarios')
        usuarios_obtenidos = cursor.fetchall()
        usuarios = []

        for usuario_obtenido in usuarios_obtenidos:
            cursor.execute('SELECT id_curriculum, plantilla FROM curriculums WHERE id_usuario = %s', (usuario_obtenido[0],))
            curriculums = cursor.fetchall()
            usuarios.append({
                'id_usuario': usuario_obtenido[0],
                'nombre': usuario_obtenido[1],
                'apellidos': usuario_obtenido[2],
                'curriculums': [{'id_curriculum': c[0], 'plantilla': c[1]} for c in curriculums]
            })

        return render_template('admin.html', usuario=current_user, usuarios=usuarios)
    except Exception as e:
        flash(f'Ha ocurrido un error: {e}')
        return redirect(url_for('perfil.perfil'))

@admin_bp.route('/admin/usuarios')
@login_required
def admin_usuarios():
    try:
        if current_user.correo == 'infocurriculum360@gmail.com':
            cursor = mysql.connection.cursor()
            cursor.execute('SELECT * FROM usuarios')
            usuarios = cursor.fetchall()
            return render_template('admin_usuarios.html', usuarios=usuarios)

        return redirect(url_for('perfil.perfil'))
    except Exception as e:
        flash(f'Ha ocurrido un error: {e}')
        return redirect(url_for('perfil.perfil'))

@admin_bp.route('/eliminar_usuario/<int:id>')
@login_required
def eliminar_usuario(id):
    try:
        cursor = mysql.connection.cursor()
        cursor.execute('DELETE FROM usuarios WHERE id = %s', (id,))
        mysql.connection.commit()
        return redirect(url_for('admin.admin'))
    except Exception:
        flash('Ha ocurrido un error')
        return redirect(url_for('admin_usuarios'))
