from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import current_user, login_required
from forms import Curriculum  # Importa tu formulario
from extensions import mysql

modificar_curriculum_bp = Blueprint('modificar_curriculum', __name__)

@modificar_curriculum_bp.route('/eliminar_curriculum/<id_curriculum>') # En la ruta de eliminar_curriculum pasamos el id del currículum que corresponda eliminar
@login_required
def eliminar_curriculum(id_curriculum):
    try:
        cursor = mysql.connection.cursor()
        cursor.execute('SELECT id_usuario FROM curriculums WHERE id_curriculum = %s', (id_curriculum,)) # Se obtiene el id del usuario que ha creado el curriculum para comprobar si es el mismo que el usuario actual
        id_usuario = cursor.fetchone()[0]
        # Verifica si el currículum pertenece al usuario actual o si el usuario actual es administrador
        if str(id_usuario) == str(current_user.id) or current_user.correo == 'infocurriculum360@gmail.com':
            # Si tiene permiso, elimina el currículum
            cursor.execute('DELETE FROM curriculums WHERE id_curriculum = %s', (id_curriculum,))
            mysql.connection.commit()
            return redirect(url_for('perfil.perfil'))
        # Si no tiene permiso, muestra un mensaje de error por pantalla
        flash('No puedes eliminar curriculums que no son tuyos.')
        return redirect(url_for('perfil.perfil'))
    except:
        # Si hay error muestra otro mensaje en pantalla
        flash('No existe ese currículum')
        return redirect(url_for('perfil.perfil'))

@modificar_curriculum_bp.route('/editar_curriculum/<id_curriculum>', methods = ['GET', 'POST']) # Pasamos el id del curriculum para que se sepa cual se tiene que editar
@login_required
def editar_curriculum(id_curriculum):
    try:
        cursor = mysql.connection.cursor()
        # Obtiene ID del usuario y plantilla del currículum
        cursor.execute('SELECT id_usuario, plantilla FROM curriculums WHERE id_curriculum = %s', (id_curriculum,))
        curriculum = cursor.fetchone()
        
        # Obtiene todos los datos del usuario
        cursor.execute('SELECT * FROM usuarios WHERE id = %s', (curriculum[0],))
        usuario_actual = cursor.fetchall()

        # Verifica que el currículum pertenezca al usuario o el usuario sea admin
        if str(curriculum[0]) == str(current_user.id) or current_user.correo == 'infocurriculum360@gmail.com':
            
            # Obtiene nombre, apellidos y correo del usuario relacionado al currículum
            cursor.execute('SELECT nombre, apellidos, correo FROM usuarios INNER JOIN curriculums ON usuarios.id = curriculums.id_usuario WHERE curriculums.id_curriculum = %s', (id_curriculum,))
            usuario = cursor.fetchone()

            # Obtiene la imagen del usuario
            cursor.execute('SELECT imagen FROM usuarios WHERE id = %s', (curriculum[0],))
            imagen = cursor.fetchone()[0]

            # Obtiene los datos generales del currículum
            cursor.execute('SELECT * FROM datos INNER JOIN curriculums ON datos.id_curriculum = curriculums.id_curriculum WHERE curriculums.id_curriculum = %s', (id_curriculum,))
            datos = cursor.fetchall()[0]
            datos_usuario = {'id_datos':datos[0], 'id_curriculum':datos[1], 'direccion':datos[2], 'telefono':datos[3], 'resumen_profesional':datos[4], 'aptitud_1':datos[5], 'aptitud_2':datos[6], 'aptitud_3':datos[7], 'aptitud_4':datos[8], 'aptitud_5':datos[9]}
            
            # Obtiene la experiencia laboral
            cursor.execute('SELECT * FROM experiencia INNER JOIN curriculums ON experiencia.id_curriculum = curriculums.id_curriculum WHERE curriculums.id_curriculum = %s', (id_curriculum,))
            experiencias = cursor.fetchall()
            experiencias_usuario = []
            for experiencia in experiencias:
                experiencias_usuario.append({'id_experiencia':experiencia[0], 'id_curriculum':experiencia[1], 'fechas':experiencia[2], 'puesto':experiencia[3], 'labor_1':experiencia[4], 'labor_2':experiencia[5], 'labor_3':experiencia[6]})
            
            # Obtiene formación
            cursor.execute('SELECT * FROM formacion INNER JOIN curriculums ON formacion.id_curriculum = curriculums.id_curriculum WHERE curriculums.id_curriculum = %s', (id_curriculum,))
            formaciones = cursor.fetchall()
            formaciones_usuario = []
            for formacion in formaciones:
                formaciones_usuario.append({'id_formacion':formacion[0], 'id_curriculum':formacion[1], 'año':formacion[2], 'titulo':formacion[3], 'temas':formacion[4]})
            
            # Prepara valores por defecto para los campos tipo input, que son los que el usuario tiene guardados en la base de datos
            parametros_por_defecto_inputs = {
                'direccion':datos_usuario['direccion'],
                'telefono':datos_usuario['telefono'],
                'experiencia_1_fechas':experiencias_usuario[0]['fechas'],
                'experiencia_1_puesto':experiencias_usuario[0]['puesto'],
                'experiencia_2_fechas':experiencias_usuario[-1]['fechas'],
                'experiencia_2_puesto':experiencias_usuario[-1]['puesto'],
                'formacion_1_año':formaciones_usuario[0]['año'],
                'formacion_1_titulo':formaciones_usuario[0]['titulo'],
                'formacion_2_año':formaciones_usuario[-1]['año'],
                'formacion_2_titulo':formaciones_usuario[-1]['titulo']
            }

            # Prepara valores por defecto para los campos tipo textarea, que son los que el usuario tiene guardados en la base de datos
            parametros_por_defecto_textareas = {
                'resumen_profesional':datos_usuario['resumen_profesional'],
                'Aptitud_1':datos_usuario['aptitud_1'],
                'Aptitud_2':datos_usuario['aptitud_2'],
                'Aptitud_3':datos_usuario['aptitud_3'],
                'Aptitud_4':datos_usuario['aptitud_4'],
                'Aptitud_5':datos_usuario['aptitud_5'],
                'experiencia_1_labor_1':experiencias_usuario[0]['labor_1'],
                'experiencia_1_labor_2':experiencias_usuario[0]['labor_2'],
                'experiencia_1_labor_3':experiencias_usuario[0]['labor_3'],
                'experiencia_2_labor_1':experiencias_usuario[-1]['labor_1'],
                'experiencia_2_labor_2':experiencias_usuario[-1]['labor_2'],
                'experiencia_2_labor_3':experiencias_usuario[-1]['labor_3'],
                'formacion_1_temas':formaciones_usuario[0]['temas'],
                'formacion_2_temas':formaciones_usuario[-1]['temas']
            }

            # Obtiene el formulario del curriculum
            formulario = Curriculum(data = parametros_por_defecto_textareas)

            # Si se envía el formulario correctamente
            if formulario.validate_on_submit and request.method == 'POST':
                # Actualiza experiencia 1
                experiencia_1_fechas = request.form.get('experiencia_1_fechas')
                experiencia_1_puesto = request.form.get('experiencia_1_puesto')
                experiencia_1_labor_1 = request.form.get('experiencia_1_labor_1')
                experiencia_1_labor_2 = request.form.get('experiencia_1_labor_2')
                experiencia_1_labor_3 = request.form.get('experiencia_1_labor_3')

                cursor.execute('SELECT id_experiencia FROM experiencia WHERE id_curriculum = %s', (id_curriculum,))
                id_experiencia = cursor.fetchall()[0][0]
                cursor.execute('UPDATE experiencia SET fechas = %s, puesto = %s, labor_1 = %s, labor_2 = %s, labor_3 = %s WHERE id_experiencia = %s', (experiencia_1_fechas, experiencia_1_puesto, experiencia_1_labor_1, experiencia_1_labor_2, experiencia_1_labor_3, id_experiencia))
                mysql.connection.commit()
                
                # Actualiza los datos generales
                datos_direccion = request.form.get('direccion')
                datos_telefono = request.form.get('telefono')
                datos_resumen_profesional = request.form.get('resumen_profesional')
                datos_aptitud_1 = request.form.get('Aptitud_1')
                datos_aptitud_2 = request.form.get('Aptitud_2')
                datos_aptitud_3 = request.form.get('Aptitud_3')
                datos_aptitud_4 = request.form.get('Aptitud_4')
                datos_aptitud_5 = request.form.get('Aptitud_5')

                cursor.execute('SELECT id_datos FROM datos WHERE id_curriculum = %s', (id_curriculum,))
                id_datos = cursor.fetchall()[0][0]
                cursor.execute('UPDATE datos SET direccion = %s, telefono = %s, resumen_profesional = %s, aptitud_1 = %s, aptitud_2 = %s, aptitud_3 = %s, aptitud_4 = %s, aptitud_5 = %s WHERE id_datos = %s', (datos_direccion, datos_telefono, datos_resumen_profesional, datos_aptitud_1, datos_aptitud_2, datos_aptitud_3, datos_aptitud_4, datos_aptitud_5, id_datos))
                mysql.connection.commit()

                # Actualiza formación 1
                formacion_1_año = request.form.get('formacion_1_año')
                formacion_1_titulo = request.form.get('formacion_1_titulo')
                formacion_1_temas = request.form.get('formacion_1_temas')

                cursor.execute('SELECT id_formacion FROM formacion WHERE id_curriculum = %s', (id_curriculum,))
                id_formacion = cursor.fetchall()[0][0]
                cursor.execute('UPDATE formacion SET año = %s, titulo = %s, temas = %s WHERE id_formacion = %s', (formacion_1_año, formacion_1_titulo, formacion_1_temas, id_formacion))
                mysql.connection.commit()

                # Obtiene el tipo de plantilla del currículum
                cursor.execute('SELECT plantilla FROM curriculums WHERE id_curriculum = %s', (id_curriculum,))
                plantilla = cursor.fetchone()[0]

                # Condicional según el tipo de plantilla actualiza formación 2
                if str(plantilla) != '1' and str(plantilla) != '2' and str(plantilla) != '3':
                    formacion_2_año = request.form.get('formacion_2_año')
                    formacion_2_titulo = request.form.get('formacion_2_titulo')
                    formacion_2_temas = request.form.get('formacion_2_temas')

                    cursor.execute('SELECT id_formacion FROM formacion WHERE id_curriculum = %s', (id_curriculum,))
                    id_formacion = cursor.fetchall()[-1][0]
                    cursor.execute('UPDATE formacion SET año = %s, titulo = %s, temas = %s WHERE id_formacion = %s', (formacion_2_año, formacion_2_titulo, formacion_2_temas, id_formacion))
                    mysql.connection.commit()

                # Si es otro tipo de plantilla, actualiza experiencia 2
                if str(plantilla) != '7' and str(plantilla) != '8' and str(plantilla) != '9':
                    print('SI QUE ENTRA')
                    experiencia_2_fechas = request.form.get('experiencia_2_fechas')
                    experiencia_2_puesto = request.form.get('experiencia_2_puesto')
                    experiencia_2_labor_1 = request.form.get('experiencia_2_labor_1')
                    experiencia_2_labor_2 = request.form.get('experiencia_2_labor_2')
                    experiencia_2_labor_3 = request.form.get('experiencia_2_labor_3')

                    cursor.execute('SELECT id_experiencia FROM experiencia WHERE id_curriculum = %s', (id_curriculum,))
                    id_experiencia = cursor.fetchall()[-1][0]
                    cursor.execute('UPDATE experiencia SET fechas = %s, puesto = %s, labor_1 = %s, labor_2 = %s, labor_3 = %s WHERE id_experiencia = %s', (experiencia_2_fechas, experiencia_2_puesto, experiencia_2_labor_1, experiencia_2_labor_2, experiencia_2_labor_3, id_experiencia))
                    mysql.connection.commit()
                cursor.close()
                # Mensaje de éxito por pantalla y redirección
                flash('Datos guardados correctamente')
                return redirect(url_for('perfil.perfil'))
            
            cursor.close()
            # Si GET o formulario no válido, renderiza plantilla con datos cargados
            return render_template('plantilla{}.html'.format(curriculum[1]), usuario = usuario, usuario_actual = usuario_actual, formulario = formulario, imagen = imagen, parametros = parametros_por_defecto_inputs)
        cursor.close()
        # Si no es propietario ni admin, aún así renderiza plantilla
        return render_template('plantilla{}.html'.format(curriculum[1]), usuario = usuario, usuario_actual = usuario_actual, formulario = formulario, imagen = imagen, parametros = parametros_por_defecto_inputs)

    except:
        flash('No puedes editar curriculums que no sean tuyos')
        return redirect(url_for('perfil.perfil'))
