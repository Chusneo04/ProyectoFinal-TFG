from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import current_user, login_required
from forms import Curriculum  # Importa tu formulario
from extensions import mysql

crear_curriculum_bp = Blueprint('crear_curriculum', __name__)

@crear_curriculum_bp.route('/elegir_plantilla')
@login_required
def elegir_plantilla():
    try:
        return render_template('elegir_plantilla.html')
    except Exception as e:
        flash('Ha ocurrido un error: {}'.format(e))
        return render_template('elegir_plantilla.html')

@crear_curriculum_bp.route('/descargar') # Para la ruta descargar
@login_required
def descargar():
    try: # Decimos un mensaje por pantalla de que la funcion descargar está en mantenimiento y redirigimos a perfil
        flash('La función descargar está en mantenimiento. Pruebe en otro momento')
        return redirect(url_for('perfil.perfil'))
    except: # Lo mismo si ocurre algun error, que no deberia 
        flash('La función descargar está en mantenimiento. Pruebe en otro momento')
        return render_template('perfil.perfil')

@crear_curriculum_bp.route('/curriculum/<plantilla>', methods = ['GET', 'POST']) #La ruta de los currículums
@login_required
def curriculum(plantilla):
    try:
        cursor = mysql.connection.cursor()
        cursor.execute('SELECT imagen FROM usuarios WHERE id = %s',(current_user.id,)) # Seleccionamos la imagen para mostrarla
        imagen = cursor.fetchone()
        imagen = imagen[0] # Accedemos a la ruta de la imagen dentro de la tupla que nos devuelve
        cursor.execute('SELECT * FROM usuarios WHERE id = %s', (current_user.id,)) # Obtenemos todos los datos del usuario actual
        usuario_actual = cursor.fetchall()


        # Estos son los parámetros por defecto que sse mostraran en cada input cuando el usuario todavia no haya escrito nada

        parametros_por_defecto_inputs = {
            'direccion':'C/Don Ramón de la Cruz, 81 Bajo D',
            'telefono':'612345678',
            'experiencia_1_fechas':'Septiembre 2015-Actual',
            'experiencia_1_puesto':'Gerente de distrito Movistar | Madrid',
            'experiencia_2_fechas':'Agosto 2005 - Septiembre 2015',
            'experiencia_2_puesto':'Gerente de operaciones ElCorteInglés | Madrid',
            'formacion_1_año':'2009',
            'formacion_1_titulo':'Máster en Administración de Empresas',
            'formacion_2_año':'2019',
            'formacion_2_titulo':'Máster en Ciencias Sociales y Humanidades'
        }


        # Estos son los parámetros por defecto que se mostraran en cada textarea cuando el usuario todavia no haya escrito nada

        parametros_por_defecto_textareas = {
            'resumen_profesional':"Gestor experimentado con excelentes aptitudes de gestión de clientes y proyectos. Orientado a la acción con gran capacidad para comunicarse de forma eficaz con público del sector tecnológico, ejecutivo y empresarial.",
            'Aptitud_1':"Gerente de compras titulado",
            'Aptitud_2':"Actitud de trabajo activa",
            'Aptitud_3':"Actualización de sistemas",
            'Aptitud_4':"Acompañamiento de confianza",
            'Aptitud_5':"Supervisión del sitio comercial",
            'experiencia_1_labor_1':"Dirigí las iniciativas de desarrollo de contratación/formación/empleados para aumentar al máximo la productividad y el potencial de los ingresos a través del desarrollo de un equipo comercial.",
            'experiencia_1_labor_2':"Planifiqué y ejecuté iniciativas de expositores promocionales en colaboración con el departamento de administración de promociones.",
            'experiencia_1_labor_3':"Me ocupé de que el establecimiento estuviera preparado para someterse a auditorías internas mediante el análisis o la preparación de controles de calidad y de estadísticas de inventario.",
            'experiencia_2_labor_1':"Supervisé las operaciones de apertura y cierre de un establecimiento con ingresos anuales de 4 millones de euros en cumplimiento con las políticas y procedimientos actuales de la empresa.",
            'experiencia_2_labor_2':"Gestioné los costes operativos encabezando el control de inventario y liderando las actividades del departamento de envío además de fijar las nóminas.",
            'experiencia_2_labor_3':"Administré los procesos financieros, incluidas las cuentas a pagar y las cuentas por cobrar mediante la gestión de una oficina de contabilidad y la actualización de los archivos del servicio de atención al cliente.",
            'formacion_1_temas':"Administración de operaciones\nUniversidad Complutense, Madrid\nTemas abordados durante el curso: oratoria y comunicación, sociología y psicología.",
            'formacion_2_temas':"Ciencias Sociales y Humanidades\nUniversidad de Salamanca\nTemas abordados durante el curso: Especialización en áreas como historia, sociología, antropología, filosofía o comunicación. "
        }

        # Obtenemos el formulario con los datos por defecto en los textareas
        curriculum = Curriculum(data = parametros_por_defecto_textareas)
        
        if int(plantilla) >= 1 and int(plantilla) <= 9: # Si el id del curriculum esta entre 1 y 9 (si no no deja porque no hay mas plantillas por ahora)
        
            # Validamos si el formulario ha sido enviado y es válido
            if curriculum.validate_on_submit and request.method == 'POST':
                # Insertamos el registro de curriculum básico
                cursor.execute('INSERT INTO curriculums(id_usuario, plantilla) VALUES(%s, %s)', (current_user.id, plantilla))
                mysql.connection.commit()
                
                cursor.execute('SELECT id_curriculum FROM curriculums ORDER BY id_curriculum DESC LIMIT 1')
                id_curriculum = cursor.fetchone()[0]

                # Recogemos datos del formulario para experiencia 1
                experiencia_1_fechas = request.form.get('experiencia_1_fechas')
                experiencia_1_puesto = request.form.get('experiencia_1_puesto')
                experiencia_1_labor_1 = request.form.get('experiencia_1_labor_1')
                experiencia_1_labor_2 = request.form.get('experiencia_1_labor_2')
                experiencia_1_labor_3 = request.form.get('experiencia_1_labor_3')

                # Guardamos en la base de datos en la tabla experiencia los datos de experiencia que introduce el usuario
                cursor.execute('INSERT INTO experiencia(id_curriculum, fechas, puesto, labor_1, labor_2, labor_3) VALUES(%s, %s, %s, %s, %s, %s)', 
                               (id_curriculum, experiencia_1_fechas, experiencia_1_puesto, experiencia_1_labor_1, experiencia_1_labor_2, experiencia_1_labor_3))
                mysql.connection.commit()

                # Recogemos datos generales
                datos_direccion = request.form.get('direccion')
                datos_telefono = request.form.get('telefono')
                datos_resumen_profesional = request.form.get('resumen_profesional')
                datos_aptitud_1 = request.form.get('Aptitud_1')
                datos_aptitud_2 = request.form.get('Aptitud_2')
                datos_aptitud_3 = request.form.get('Aptitud_3')
                datos_aptitud_4 = request.form.get('Aptitud_4')
                datos_aptitud_5 = request.form.get('Aptitud_5')

                # Guardamos en la base de datos en la tabla datos los datos que introduce el usuario
                cursor.execute('INSERT INTO datos(id_curriculum, direccion, telefono, resumen_profesional, aptitud_1, aptitud_2, aptitud_3, aptitud_4, aptitud_5) VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s)', 
                               (id_curriculum, datos_direccion, datos_telefono, datos_resumen_profesional, datos_aptitud_1, datos_aptitud_2, datos_aptitud_3, datos_aptitud_4, datos_aptitud_5))
                mysql.connection.commit()

                # Recogemos datos de formación 1
                formacion_1_año = request.form.get('formacion_1_año')
                formacion_1_titulo = request.form.get('formacion_1_titulo')
                formacion_1_temas = request.form.get('formacion_1_temas')

                # Guardamos en la base de datos en la tabla formacion los datos de formacion que introduce el usuario
                cursor.execute('INSERT INTO formacion(id_curriculum, año, titulo, temas) VALUES (%s, %s, %s, %s)', 
                               (id_curriculum, formacion_1_año, formacion_1_titulo, formacion_1_temas))
                mysql.connection.commit()

                # Si la plantilla no es una de las 3 que no tiene una segunda formacion
                if str(plantilla) != '1' and str(plantilla) != '2' and str(plantilla) != '3':
                    #Obtiene todos los datos que el usuario introduce
                    formacion_2_año = request.form.get('formacion_2_año')
                    formacion_2_titulo = request.form.get('formacion_2_titulo')
                    formacion_2_temas = request.form.get('formacion_2_temas')

                    # Y los guarda en la BD
                    cursor.execute('INSERT INTO formacion(id_curriculum, año, titulo, temas) VALUES (%s, %s, %s, %s)', 
                                   (id_curriculum, formacion_2_año, formacion_2_titulo, formacion_2_temas))
                    mysql.connection.commit()

                # Si la plantilla no es una de las 3 que no tiene una segunda experiencia
                if str(plantilla) != '7' and str(plantilla) != '8' and str(plantilla) != '9':

                    #Obtiene todos los datos que el usuario introduce

                    experiencia_2_fechas = request.form.get('experiencia_2_fechas')
                    experiencia_2_puesto = request.form.get('experiencia_2_puesto')
                    experiencia_2_labor_1 = request.form.get('experiencia_2_labor_1')
                    experiencia_2_labor_2 = request.form.get('experiencia_2_labor_2')
                    experiencia_2_labor_3 = request.form.get('experiencia_2_labor_3')

                    # Y los guarda en la BD
                    cursor.execute('INSERT INTO experiencia(id_curriculum, fechas, puesto, labor_1, labor_2, labor_3) VALUES(%s, %s, %s, %s, %s, %s)', 
                                   (id_curriculum, experiencia_2_fechas, experiencia_2_puesto, experiencia_2_labor_1, experiencia_2_labor_2, experiencia_2_labor_3))
                    mysql.connection.commit()
                cursor.close()    
                return redirect(url_for('perfil.perfil'))
            
            # Renderiza la plantilla elegida devolviendo todos los datos necesarios para que el frontend los gestione
            return render_template('plantilla{}.html'.format(plantilla), 
                                   usuario_actual = usuario_actual, curriculum_id = id, usuario = current_user, 
                                   imagen = imagen, formulario = curriculum, parametros = parametros_por_defecto_inputs)
        
        return redirect(url_for('crear_curriculum.elegir_plantilla'))
    
    except:
        print('Ha ocurrido un error')
        return redirect(url_for('perfil.perfil'))
