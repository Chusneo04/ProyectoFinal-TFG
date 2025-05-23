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

@crear_curriculum_bp.route('/curriculum/<plantilla>', methods = ['GET', 'POST'])
@login_required
def curriculum(plantilla):
    try:
        cursor = mysql.connection.cursor()
        cursor.execute('SELECT imagen FROM usuarios WHERE id = %s',(current_user.id,))
        imagen = cursor.fetchone()
        imagen = imagen[0]
        print('Hola')
        flash(imagen)
        cursor.execute('SELECT * FROM usuarios WHERE id = %s', (current_user.id,))
        usuario_actual = cursor.fetchall()
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
        curriculum = Curriculum(data = parametros_por_defecto_textareas)
        if int(plantilla) >= 1 and int(plantilla) <= 9:
            if curriculum.validate_on_submit and request.method == 'POST':
                cursor.execute('INSERT INTO curriculums(id_usuario, plantilla) VALUES(%s, %s)', (current_user.id, plantilla))
                mysql.connection.commit()
                
                cursor.execute('SELECT id_curriculum FROM curriculums ORDER BY id_curriculum DESC LIMIT 1')
                
                id_curriculum = cursor.fetchone()[0]
                
                

                experiencia_1_fechas = request.form.get('experiencia_1_fechas')
                experiencia_1_puesto = request.form.get('experiencia_1_puesto')
                experiencia_1_labor_1 = request.form.get('experiencia_1_labor_1')
                experiencia_1_labor_2 = request.form.get('experiencia_1_labor_2')
                experiencia_1_labor_3 = request.form.get('experiencia_1_labor_3')

                cursor.execute('INSERT INTO experiencia(id_curriculum, fechas, puesto, labor_1, labor_2, labor_3) VALUES(%s, %s, %s, %s, %s, %s)', (id_curriculum, experiencia_1_fechas, experiencia_1_puesto, experiencia_1_labor_1, experiencia_1_labor_2, experiencia_1_labor_3))
                mysql.connection.commit()

                datos_direccion = request.form.get('direccion')
                datos_telefono = request.form.get('telefono')
                datos_resumen_profesional = request.form.get('resumen_profesional')
                datos_aptitud_1 = request.form.get('Aptitud_1')
                datos_aptitud_2 = request.form.get('Aptitud_2')
                datos_aptitud_3 = request.form.get('Aptitud_3')
                datos_aptitud_4 = request.form.get('Aptitud_4')
                datos_aptitud_5 = request.form.get('Aptitud_5')

                cursor.execute('INSERT INTO datos(id_curriculum, direccion, telefono, resumen_profesional, aptitud_1, aptitud_2, aptitud_3, aptitud_4, aptitud_5) VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s)', (id_curriculum, datos_direccion, datos_telefono, datos_resumen_profesional, datos_aptitud_1, datos_aptitud_2, datos_aptitud_3, datos_aptitud_4, datos_aptitud_5))
                mysql.connection.commit()

                formacion_1_año = request.form.get('formacion_1_año')
                formacion_1_titulo = request.form.get('formacion_1_titulo')
                formacion_1_temas = request.form.get('formacion_1_temas')

                cursor.execute('INSERT INTO formacion(id_curriculum, año, titulo, temas) VALUES (%s, %s, %s, %s)', (id_curriculum, formacion_1_año, formacion_1_titulo, formacion_1_temas))
                mysql.connection.commit()


                if int(id_curriculum) != 1 and int(id_curriculum) != 2 and int(id_curriculum) != 3:
                    formacion_2_año = request.form.get('formacion_2_año')
                    formacion_2_titulo = request.form.get('formacion_2_titulo')
                    formacion_2_temas = request.form.get('formacion_2_temas')

                    cursor.execute('INSERT INTO formacion(id_curriculum, año, titulo, temas) VALUES (%s, %s, %s, %s)', (id_curriculum, formacion_2_año, formacion_2_titulo, formacion_2_temas))
                    mysql.connection.commit()
 
                elif int(id_curriculum) != 7 and int(id_curriculum) != 8 and int(id_curriculum) != 9:
                    experiencia_2_fechas = request.form.get('experiencia_2_fechas')
                    experiencia_2_puesto = request.form.get('experiencia_2_puesto')
                    experiencia_2_labor_1 = request.form.get('experiencia_2_labor_1')
                    experiencia_2_labor_2 = request.form.get('experiencia_2_labor_2')
                    experiencia_2_labor_3 = request.form.get('experiencia_2_labor_3')

                    cursor.execute('INSERT INTO experiencia(id_curriculum, fechas, puesto, labor_1, labor_2, labor_3) VALUES(%s, %s, %s, %s, %s, %s)', (id_curriculum, experiencia_2_fechas, experiencia_2_puesto, experiencia_2_labor_1, experiencia_2_labor_2, experiencia_2_labor_3))
                    mysql.connection.commit()



                return render_template('plantilla{}.html'.format(plantilla), usuario_actual = usuario_actual, curriculum_id = id, usuario = current_user, imagen = imagen, formulario = curriculum, parametros = parametros_por_defecto_inputs)
            return render_template('plantilla{}.html'.format(plantilla), usuario_actual = usuario_actual, curriculum_id = id, usuario = current_user, imagen = imagen, formulario = curriculum, parametros = parametros_por_defecto_inputs)
        return redirect(url_for('crear_curriculum.elegir_plantilla'))
    except Exception as e:
        print('Error: {}'.format(e))
        return(redirect(url_for('perfil.perfil')))