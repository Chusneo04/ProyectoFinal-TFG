from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from extensions import mysql
from models import User  # Importa el modelo de usuario

# Creamos la variable del blueprint

admin_bp = Blueprint('admin', __name__)

# Creamos la ruta de admin

@admin_bp.route('/admin')
@login_required # Indicamos que debe estar logueado el usuario para entrar
def admin():
    try:
        if current_user.correo != 'infocurriculum360@gmail.com': # Comprobamos si el correo del usuario actual es el del admin, si no lo es le redirige al perfil correspondiente
            return redirect(url_for('perfil.perfil'))
        
        cursor = mysql.connection.cursor()
        cursor.execute('SELECT id, nombre, apellidos FROM usuarios') # Obtenemos el id, el nombre y los apellidos de todos los usuarios
        usuarios_obtenidos = cursor.fetchall()
        usuarios = []

        for usuario_obtenido in usuarios_obtenidos: # Para cada usuario que hemos extraido de la base de datos, obtenemos todos sus currículums
            cursor.execute('SELECT id_curriculum, plantilla FROM curriculums WHERE id_usuario = %s', (usuario_obtenido[0],))
            curriculums = cursor.fetchall()
            lista_curriculums = [] # Creamos la lista de los currículums
            for curriculum in curriculums: # Una vez obtenidos todos los currículums del usuario los metemos en la lista
                lista_curriculums.append({
                    'id_curriculum': curriculum[0],
                    'plantilla': curriculum[1]
                }) # Introducimos cada uno en la lista

                # Ahora añadimos cada dato del usuario y sus currículums son la lista de curriculums creada justo arriba ya con todos sus currículums dentro
                usuarios.append({
                    'id_usuario': usuario_obtenido[0],
                    'nombre': usuario_obtenido[1],
                    'apellidos': usuario_obtenido[2],
                    'curriculums': lista_curriculums
                })

            

        return render_template('admin.html', usuario=current_user, usuarios=usuarios) # Muestra la plantilla de administración
    except: # Si algo va mal salta un error y redirige a la interfaz de perfil con un mensaje de qque ha ocurrido un error
        flash('Ha ocurrido un error')
        return redirect(url_for('perfil.perfil'))

@admin_bp.route('/admin/usuarios') # Creamos la lista admin/usuarios
@login_required # Indicamos que tiene que estar autenticado para poder acceder
def admin_usuarios():
    try:
        if current_user.correo == 'infocurriculum360@gmail.com': # Comprobamos que el correo del usuarrio actual es el mismo que el correo del usuario administrador
            cursor = mysql.connection.cursor()
            cursor.execute('SELECT * FROM usuarios') # Obtenemos todos los usuarios de la base de datos
            usuarios = cursor.fetchall()
            return render_template('admin_usuarios.html', usuarios=usuarios) # Redirigimos a la interfaz de admin_usuarios y enviamos al frontend los datos de los usuarios para que los pueda mostrar

        return redirect(url_for('perfil.perfil')) # En caso de que el usuario no sea el administrador redirije a perfil
    except: #Redirige a perfil con un mensaje de error por pantalla en caso de que algo no vaya como corresponde
        flash('Ha ocurrido un error')
        return redirect(url_for('perfil.perfil')) 

@admin_bp.route('/eliminar_usuario/<int:id>') # Creamos la ruta de eliminar usuarios, le pasamos el id del usuario para que sepa con cual tiene que trabajar
@login_required # Se obliga que esté el usuario autenticado
def eliminar_usuario(id):
    try:
        if current_user.correo == 'infocurriculum360@gmail.com': # Comprobamos que el correo del usuarrio actual es el mismo que el correo del usuario administrador

            cursor = mysql.connection.cursor()
            if str(id) != str(current_user.id): # Se comprueba que no es el id el mismo que el del usuario actual que debe ser el del admin
                cursor.execute('DELETE FROM usuarios WHERE id = %s', (id,)) # Se borra el usuario introducido de la base de datos
                mysql.connection.commit()
                return redirect(url_for('admin.admin')) # Y redirige a admin
            # Si se intenta borrar el usuario administrador se impide y lanza un mensaje de que no se puede borrar, redirigiendo a admin
            flash('No se puede borrar el usuario administrador')
            return redirect(url_for('admin.admin'))
        return redirect(url_for('perfil.perfil')) # Si el usuario actual no es el de admin impide realizar cualquier accion y redirige a perfil
    except: # Si ocurre algun error redirige a admin_usuarios y se muestra por pantalla un mensaje de error
        flash('Ha ocurrido un error')
        return redirect(url_for('admin_usuarios'))
