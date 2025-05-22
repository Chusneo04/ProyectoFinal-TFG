from flask import Flask, redirect, render_template, request, url_for, flash
import os
from flask_mysqldb import MySQL
from datetime import datetime
from dotenv import load_dotenv
from forms import Usuario_register, Usuario_login, Recuperar_clave_email, Nueva_Clave, Editar_perfil, Editar_clave, Clave_nueva, Contacto, Curriculum
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from flask_login import LoginManager, UserMixin, login_user, login_required, current_user, logout_user
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from secrets import token_urlsafe

app = Flask(__name__)

load_dotenv()
mysql = MySQL(app)

#Aqui tenemos la "configuracion" de las credenciales que estan en el .env para acceder a la base de datos

app.config['MYSQL_HOST'] = os.getenv('MYSQL_HOST')
app.config['MYSQL_USER'] = os.getenv('MYSQL_USER')
app.config['MYSQL_PASSWORD'] = os.getenv('MYSQL_PASSWORD')
app.config['MYSQL_DB'] = os.getenv('MYSQL_DB')
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')

carpeta_de_subida = './src/static/img'
app.config['UPLOAD_FOLDER'] = carpeta_de_subida

extensiones_permitidas = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in extensiones_permitidas

#Aqui definimos el objeto del usuario para usarlo mas adelante

class User(UserMixin):
    def __init__(self, id, nombre, apellidos, correo, clave, fecha, token):
        self.id = str(id)
        self.nombre = nombre
        self.apellidos = apellidos
        self.correo = correo
        self.clave = clave
        self.fecha = fecha
        self.token = token

login_manager = LoginManager()
login_manager.init_app(app)

#Aqui tenemos la funcion con la que se carga el usuario para poder gestionar la sesión

@login_manager.user_loader
def load_user(id):
    try:
        cursor = mysql.connection.cursor() #Aqui abrimos el cursor de la base de datos
        cursor.execute("SELECT id, nombre, apellidos, correo, clave, fecha_de_creacion, token FROM usuarios WHERE id = %s", (id,)) #Aqui obtenemos el usuario para comprobar si existe en la base de datos
        user = cursor.fetchone() #Aqui se introducen en una variable los campos que le hemos pedido sobre el usuario en la linea anterior
        cursor.close() #Cerramos el cursor

    #En las 3 siguientes lineas gestionamos una excepcion para que en caso de haber cualquier tipo de error en la busqueda del usuario nos devuelva un mensaje de error
    except Exception as error:
        flash("Error al cargar usuario")
        return None
    
    #Aqui nos devuelve el usuario en caso de que haya salido todo correcto y sin que haya saltado la excepción anterior
    if user:
        return User(user[0], user[1], user[2], user[3], user[4], user[5], user[6])
    return None


@app.route('/')
def index():
    return render_template('index.html')


#Esta es la funcion de la interfaz de registro

@app.route('/register', methods = ['GET', 'POST'])
def register():

    try:
        #Aqui comprobamos si el usuario ya esta autenticado, si lo está te redirije a la interfaz de perfil

        if current_user.is_authenticated:
            return redirect(url_for('perfil'))


        cursor = mysql.connection.cursor()
        usuario = Usuario_register() #Aqui traemos el formulario para llevar a cabo el registro del usuario
        
        #Si todos los campos del formulario se han validado correctamente 

        if usuario.validate_on_submit and request.method == 'POST':

            #Obtenemos todos los datos sobre el usuario para almacenarlo en la base de datos en caso de que no exista previamente

            nombre = request.form.get('nombre')
            apellidos = request.form.get('apellidos')
            correo = request.form.get('correo')
            clave = request.form.get('clave')
            clave = generate_password_hash(clave)
            fecha = datetime.now()
            token = None

            cursor.execute('SELECT * FROM usuarios WHERE correo = %s', (correo,)) #Aqui comprobamos si el usuario existe ya en la base de datos
            usuario_existente = cursor.fetchone()

            #Aqui le mostramos un mensaje al usuario en caso de que ya esté registrado anteriormente

            if usuario_existente:
                flash('El usuario ya existe')

            #Aqui llevamos a cabo el registro del nuevo usuario
            else:
                #Introducimos al usuario en la base de datos con los campos correspondientes
                cursor.execute('INSERT INTO usuarios(nombre, apellidos, correo, clave, fecha_de_creacion, token, imagen) VALUES (%s, %s, %s, %s, %s, %s, %s)', (nombre, apellidos, correo, clave, fecha, token, '../static/img/user.png'))
                mysql.connection.commit() #Guardamos los cambios
                print('110')
                #Obtenemos el nuevo usuario una vez ya está registrado en la base de datos

                cursor.execute('SELECT id, nombre, apellidos, correo, clave, fecha_de_creacion, token FROM usuarios WHERE correo = %s', (correo,))
                nuevo_usuario = cursor.fetchone()
                print('111')
                #Y aqui ya llevamos a cabo el inicio de sesión para que pueda acceder a las rutas protegidas
                if nuevo_usuario:
                    print('Hola')
                    usuario_obj = User(nuevo_usuario[0], nuevo_usuario[1], nuevo_usuario[2], nuevo_usuario[3], nuevo_usuario[4], nuevo_usuario[5], nuevo_usuario[6])
                    print('Adios')
                    print(type(nuevo_usuario[3]))
                    login_user(usuario_obj)
                    print('112')
                    #Preparamos las credenciales del correo para poder enviar correos

                    servidor_smtp = "smtp.gmail.com"
                    puerto_smtp = 587
                    usuario_smtp = "infocurriculum360@gmail.com"
                    clave_smtp = os.getenv('EMAIL_KEY')
                    print("Clave SMTP obtenida:", clave_smtp)

                    #Preparamos el mensaje para enviarlo por correo

                    msg = MIMEMultipart()
                    msg['From'] = usuario_smtp
                    msg['To'] = nuevo_usuario[3]
                    msg['Subject'] = "Bienvenido {}".format(nuevo_usuario[1])
                    mensaje = "¡Bienvenido/a a Curriculum360! Nos alegra que formes parte de nuestra comunidad.Aquí encontrarás herramientas para mejorar tu perfil profesional, organizar tu experiencia y destacar tu talento. Nos comprometemos a ayudarte en cada paso del camino."
                    msg.attach(MIMEText(mensaje, "plain")) #Esto introduce el mensaje de la linea superior en el cuerpo del correo
                    try:
                        with smtplib.SMTP(servidor_smtp, puerto_smtp) as server:
                            server.starttls() #Iniciamos la conexion con seguridad 
                            server.login(usuario_smtp, clave_smtp) #Iniciamos sesion en el correo
                            server.sendmail(usuario_smtp, msg["To"], msg.as_string()) #Enviamos el mensaje de bienvenida al nuevo usuario
                            print("Correo enviado correctamente")
                            return redirect(url_for('perfil')) #Si todo va bien redirigirá al usuario a la interfaz de perfil
                    except Exception as e:
                        print("Error al enviar correo: {}".format(e))
                        return render_template('register.html', usuario=usuario)


                    
                return render_template('register.html', usuario=usuario) #Si algo falla te vuelve a mostrar la de registro

        return render_template('register.html', usuario=usuario) #Muestra la interfaz de registro y envia al html el formulario para gestionar alli el diseño   

    except:
        flash('Error al registrar')
        return render_template('register.html', usuario=usuario)

@app.route('/login', methods=['GET', 'POST'])
def login():
    try:
        #Aqui comprobamos si el usuario ya esta autenticado, si lo está te redirije a la interfaz de perfil

        if current_user.is_authenticated:
            return redirect(url_for('perfil'))


        cursor = mysql.connection.cursor()
        usuario = Usuario_login() #Aqui traemos el formulario para llevar a cabo el registro del usuario

        #Si todos los campos del formulario se han validado correctamente 

        if usuario.validate_on_submit and request.method == 'POST':

            #Obtenemos todos los datos sobre el usuario para proceder al inicio de sesión

            correo = request.form.get('correo')
            clave = request.form.get('clave')

            cursor.execute('SELECT * FROM usuarios WHERE correo = %s', (correo,)) #Aqui comprobamos si el usuario existe ya en la base de datos
            usuario_existente = cursor.fetchone()

            #Aqui le mostramos un mensaje al usuario en caso de que no esté registrado

            if not usuario_existente:
                flash('Las credenciales introducidas son incorrectas')
                return render_template('login.html', usuario=usuario)
                
            else:
                #Y aqui ya llevamos a cabo el inicio de sesión para que pueda acceder a las rutas protegidas
                print('192')
                if check_password_hash(usuario_existente[4], clave):
                    print('194')
                    usuario_obj = User(usuario_existente[0], usuario_existente[1], usuario_existente[2], usuario_existente[3], usuario_existente[4], usuario_existente[5], usuario_existente[6])
                    print('196')
                    login_user(usuario_obj)
                    print('198')
                    return redirect(url_for('perfil')) #Si todo va bien redirige al usuario a la interfaz de perfil 
                else:
                    flash('Las credenciales introducidas son incorrectas')
                    return render_template('login.html', usuario=usuario)
        return render_template('login.html', usuario=usuario) #Muestra la interfaz de login y envia al html el formulario para gestionar alli el diseño   

    except:
        flash('Error al Iniciar sesión')
        return render_template('login.html', usuario=usuario)


@app.route('/recuperar_clave', methods = ['GET', 'POST'])
def recuperar_clave():
    try:
        if current_user.is_authenticated:
            return redirect(url_for('perfil'))
        
        cursor = mysql.connection.cursor()
        formulario_email = Recuperar_clave_email()

        if formulario_email.validate_on_submit and request.method == 'POST':
            correo = request.form.get('correo')
            cursor.execute('SELECT * FROM usuarios WHERE correo = %s', (correo,))
            usuario_existe = cursor.fetchone()
            print(usuario_existe)
            if not usuario_existe:
                flash('El usuario no existe')
                return render_template('recuperar_contraseña.html', formulario = formulario_email)
            
            else:
                token = token_urlsafe(32)
                print(token)
                cursor = mysql.connection.cursor()
                cursor.execute('UPDATE usuarios SET token = %s WHERE correo = %s', (token, correo))
                mysql.connection.commit()
                reset_url = url_for('nueva_clave', token = token, _external = True)

                #Preparamos las credenciales del correo para poder enviar correos

                servidor_smtp = "smtp.gmail.com"
                puerto_smtp = 587
                usuario_smtp = "infocurriculum360@gmail.com"
                clave_smtp = os.getenv('EMAIL_KEY')

                #Preparamos el mensaje para enviarlo por correo

                msg = MIMEMultipart()
                msg['From'] = usuario_smtp
                msg['To'] = correo
                msg['Subject'] = "Recuperación de contraseña"
                mensaje = "Para recuperar la contraseña accede al siguiente enlace: {}".format(reset_url)
                msg.attach(MIMEText(mensaje, "plain")) #Esto introduce el mensaje de la linea superior en el cuerpo del correo
                try:
                    with smtplib.SMTP(servidor_smtp, puerto_smtp) as server:
                        server.starttls() #Iniciamos la conexion con seguridad 
                        server.login(usuario_smtp, clave_smtp) #Iniciamos sesion en el correo
                        server.sendmail(usuario_smtp, msg["To"], msg.as_string()) #Enviamos el mensaje de bienvenida al nuevo usuario
                        flash("Correo enviado correctamente")
                        return render_template('recuperar_contraseña.html', formulario = formulario_email)  
                     
                except Exception as e:
                    flash("Error al enviar correo: {}".format(e))
                    return render_template('recuperar_contraseña.html', formulario = formulario_email)
    except Exception as e:
        flash('Ha ocurrido un error, {}'.format(e))
        return render_template('recuperar_contraseña.html', formulario = formulario_email)
    return render_template('recuperar_contraseña.html', formulario = formulario_email)


@app.route('/nueva_clave/<token>', methods = ['GET', 'POST'])
def nueva_clave(token):

    try:
        if current_user.is_authenticated:
            return redirect(url_for('perfil'))
        cursor = mysql.connection.cursor()
        cursor.execute('SELECT * FROM usuarios WHERE token = %s', (token,))
        usuario_existe = cursor.fetchone()

        if not usuario_existe:
            flash('El enlace ha caducado')
            return redirect(url_for('recuperar_clave'))
        else:
            formulario = Nueva_Clave()

            if formulario.validate_on_submit and request.method == 'POST':
                clave = request.form.get('contraseña')
                clave_confirmada = request.form.get('confirmar_clave')

                if clave != clave_confirmada:
                    flash('Las contraseñas no coinciden')
                    return render_template('nueva_clave.html', formulario = formulario)

                clave = generate_password_hash(clave)
                cursor.execute('UPDATE usuarios SET clave = %s WHERE token = %s', (clave, token))
                mysql.connection.commit()
                cursor.execute('UPDATE usuarios SET token = %s WHERE token = %s', (None, token))
                mysql.connection.commit()
                return redirect(url_for('login'))
    except Exception as e:
        flash('Ha ocurrido un error')
        return render_template('nueva_clave.html', formulario = formulario)
    return render_template('nueva_clave.html', formulario = formulario)

#Esta es la funcion de la interfaz de perfil

@app.route('/perfil')
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

#Esta es la funcion que cierra la sesión para que el usuario pueda acceder a las rutas en las que no puedes tener una sesion iniciada

@app.route('/editar_perfil', methods = ['GET', 'POST'])
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
                filepath = os.path.normpath(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                print(filepath)
                print("Ruta donde se intentará guardar el archivo:", os.path.abspath(filepath))
                file.save(filepath)
                ruta_imagen_bd = '../static/img/{}'.format(filename)
                print(ruta_imagen_bd)
            cursor = mysql.connection.cursor()
            cursor.execute('UPDATE usuarios SET nombre = %s, apellidos = %s, correo = %s, imagen = %s WHERE id = %s', (nombre, apellidos, correo, ruta_imagen_bd, id))
            mysql.connection.commit()
            flash('Datos actualizados correctamente')
            return redirect(url_for('perfil'))

        return render_template('editar_perfil.html', usuario = current_user, formulario = formulario)
    except Exception as e:
        flash('Ha ocurrido un error: {}'.format(e))
        return render_template('editar_perfil.html', usuario = current_user, formulario = formulario)

@app.route('/editar_clave', methods = ['GET', 'POST'])
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
                return redirect(url_for('clave_nueva'))
            flash('La contraseña introducida no es correcta')
        return render_template('editar_clave.html', formulario = formulario, usuario = current_user)
    except Exception as e:
        flash('Ha ocurrrido un error: {}'.format(e))
        return render_template('editar_clave.html', formulario = formulario, usuario = current_user)

@app.route('/clave_nueva', methods = ['GET', 'POST'])
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
            return redirect(url_for('perfil'))
    except Exception as e:
        flash('Ha ocurrido un error')
        return render_template('clave_nueva.html', formulario = formulario)
    return render_template('clave_nueva.html', formulario = formulario)

@app.route('/contacto', methods = ['GET', 'POST'])
def contacto():
    try:
        formulario = Contacto()
        if current_user.is_authenticated:
                nombre = current_user.nombre
                correo = current_user.correo
                volver = '/perfil'
        else:
            nombre = ''
            correo = ''
            volver = '/'
        if formulario.validate_on_submit and request.method == 'POST':
            if current_user.is_authenticated:
                nombre = current_user.nombre
                correo = current_user.correo
                volver = '/perfil'
            else:
                nombre = request.form.get('nombre')
                correo = request.form.get('correo')
                volver = '/'
            
            mensaje_formulario = request.form.get('mensaje')
            #Preparamos las credenciales del correo para poder enviar correos

            servidor_smtp = "smtp.gmail.com"
            puerto_smtp = 587
            usuario_smtp = "infocurriculum360@gmail.com"
            clave_smtp = os.getenv('EMAIL_KEY')

            #Preparamos el mensaje para enviarlo por correo

            msg = MIMEMultipart()
            msg['From'] = usuario_smtp
            msg['To'] = usuario_smtp
            msg['Subject'] = "Mensaje de {}".format(nombre)
            mensaje = "{}\nAqui les dejo mi correo electrónico: {}".format(mensaje_formulario, correo)
            msg.attach(MIMEText(mensaje, "plain")) #Esto introduce el mensaje de la linea superior en el cuerpo del correo
            try:
                with smtplib.SMTP(servidor_smtp, puerto_smtp) as server:
                    server.starttls() #Iniciamos la conexion con seguridad 
                    server.login(usuario_smtp, clave_smtp) #Iniciamos sesion en el correo
                    server.sendmail(usuario_smtp, msg["To"], msg.as_string()) #Enviamos el mensaje de bienvenida al nuevo usuario
                    flash("Correo enviado correctamente")
                    return render_template('contacto.html', formulario = formulario, nombre = nombre, correo = correo, boton_volver = volver)  
                    
            except Exception as e:
                flash("Error al enviar correo: {}".format(e))
                return render_template('contacto.html', formulario = formulario, nombre = nombre, correo = correo, boton_volver = volver) 

        return render_template('contacto.html', formulario = formulario, nombre = nombre, correo = correo, boton_volver = volver)
    except Exception as e:
        flash('Ha ocurrido un error: {}'.format(e))
        return render_template('contacto.html', formulario = formulario, nombre = nombre, correo = correo, boton_volver = volver)

@app.route('/elegir_plantilla')
@login_required
def elegir_plantilla():
    try:
        return render_template('elegir_plantilla.html')
    except Exception as e:
        flash('Ha ocurrido un error: {}'.format(e))
        return render_template('elegir_plantilla.html')

@app.route('/curriculum/<plantilla>', methods = ['GET', 'POST'])
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
        return redirect(url_for('elegir_plantilla'))
    except Exception as e:
        print('Error: {}'.format(e))
        return(redirect(url_for('perfil')))

@app.route('/eliminar_curriculum/<id_curriculum>')
@login_required
def eliminar_curriculum(id_curriculum):
    try:
        cursor = mysql.connection.cursor()
        cursor.execute('SELECT id_usuario FROM curriculums WHERE id_curriculum = %s', (id_curriculum,))
        id_usuario = cursor.fetchone()
        if id_usuario == current_user.id or current_user.correo == 'infocurriculum360@gmail.com':
            cursor.execute('DELETE FROM curriculums WHERE id_curriculum = %s', (id_curriculum,))
            mysql.connection.commit()
            return redirect(url_for('perfil'))
        flash('No puedes eliminar curriculums que no son tuyos.')
        return redirect(url_for('perfil'))
    except Exception as e:
        flash(e)
        return redirect(url_for('perfil'))

@app.route('/editar_curriculum/<id_curriculum>', methods = ['GET', 'POST'])
@login_required
def editar_curriculum(id_curriculum):
    try:
        cursor = mysql.connection.cursor()
        cursor.execute('SELECT id_usuario, plantilla FROM curriculums WHERE id_curriculum = %s', (id_curriculum,))
        curriculum = cursor.fetchone()
        cursor.execute('SELECT * FROM usuarios WHERE id = %s', (curriculum[0],))
        usuario_actual = cursor.fetchall()
        print('HOLA')
        print(curriculum[0])
        print(current_user.id)
        if str(curriculum[0]) == str(current_user.id) or current_user.correo == 'infocurriculum360@gmail.com':
            
            
            
            
            cursor.execute('SELECT nombre, apellidos, correo FROM usuarios INNER JOIN curriculums ON usuarios.id = curriculums.id_usuario WHERE curriculums.id_curriculum = %s', (id_curriculum,))
            usuario = cursor.fetchone()

            cursor.execute('SELECT imagen FROM usuarios WHERE id = %s', (curriculum[0],))
            imagen = cursor.fetchone()
            imagen = imagen[0]

            cursor.execute('SELECT * FROM datos INNER JOIN curriculums ON datos.id_curriculum = curriculums.id_curriculum WHERE curriculums.id_curriculum = %s', (id_curriculum,))
            datos = cursor.fetchall()
            datos = datos[0]
            datos_usuario = {'id_datos':datos[0], 'id_curriculum':datos[1], 'direccion':datos[2], 'telefono':datos[3], 'resumen_profesional':datos[4], 'aptitud_1':datos[5], 'aptitud_2':datos[6], 'aptitud_3':datos[7], 'aptitud_4':datos[8], 'aptitud_5':datos[9]}
            
            cursor.execute('SELECT * FROM experiencia INNER JOIN curriculums ON experiencia.id_curriculum = curriculums.id_curriculum WHERE curriculums.id_curriculum = %s', (id_curriculum,))
            experiencias = cursor.fetchall()
            experiencias_usuario = []
            for experiencia in experiencias:
                experiencias_usuario.append({'id_experiencia':experiencia[0], 'id_curriculum':experiencia[1], 'fechas':experiencia[2], 'puesto':experiencia[3], 'labor_1':experiencia[4], 'labor_2':experiencia[5], 'labor_3':experiencia[6]})
            
            cursor.execute('SELECT * FROM formacion INNER JOIN curriculums ON formacion.id_curriculum = curriculums.id_curriculum WHERE curriculums.id_curriculum = %s', (id_curriculum,))
            formaciones = cursor.fetchall()
            formaciones_usuario = []
            for formacion in formaciones:
                formaciones_usuario.append({'id_formacion':formacion[0], 'id_curriculum':formacion[1], 'año':formacion[2], 'titulo':formacion[3], 'temas':formacion[4]})
            

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
            formulario = Curriculum(data = parametros_por_defecto_textareas)
            if formulario.validate_on_submit and request.method == 'POST':
                experiencia_1_fechas = request.form.get('experiencia_1_fechas')
                experiencia_1_puesto = request.form.get('experiencia_1_puesto')
                experiencia_1_labor_1 = request.form.get('experiencia_1_labor_1')
                experiencia_1_labor_2 = request.form.get('experiencia_1_labor_2')
                experiencia_1_labor_3 = request.form.get('experiencia_1_labor_3')

                cursor.execute('SELECT id_experiencia FROM experiencia WHERE id_curriculum = %s', (id_curriculum,))
                
                id_experiencia = cursor.fetchall()[0][0]
                cursor.execute('UPDATE experiencia SET fechas = %s, puesto = %s, labor_1 = %s, labor_2 = %s, labor_3 = %s WHERE id_experiencia = %s', (experiencia_1_fechas, experiencia_1_puesto, experiencia_1_labor_1, experiencia_1_labor_2, experiencia_1_labor_3, id_experiencia))
                mysql.connection.commit()
                

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

                formacion_1_año = request.form.get('formacion_1_año')
                formacion_1_titulo = request.form.get('formacion_1_titulo')
                formacion_1_temas = request.form.get('formacion_1_temas')

                cursor.execute('SELECT id_formacion FROM formacion WHERE id_curriculum = %s', (id_curriculum,))
                id_formacion = cursor.fetchall()[0][0]
                cursor.execute('UPDATE formacion SET año = %s, titulo = %s, temas = %s WHERE id_formacion = %s', (formacion_1_año, formacion_1_titulo, formacion_1_temas, id_formacion))
                mysql.connection.commit()

                if int(id_curriculum) != 1 and int(id_curriculum) != 2 and int(id_curriculum) != 3:
                    formacion_2_año = request.form.get('formacion_2_año')
                    formacion_2_titulo = request.form.get('formacion_2_titulo')
                    formacion_2_temas = request.form.get('formacion_2_temas')

                    cursor.execute('SELECT id_formacion FROM formacion WHERE id_curriculum = %s', (id_curriculum,))
                    id_formacion = cursor.fetchall()[-1][0]
                    cursor.execute('UPDATE formacion SET año = %s, titulo = %s, temas = %s WHERE id_formacion = %s', (formacion_2_año, formacion_2_titulo, formacion_2_temas, id_formacion))
                    mysql.connection.commit()
                    

                elif int(id_curriculum) != 7 and int(id_curriculum) != 8 and int(id_curriculum) != 9:
                    experiencia_2_fechas = request.form.get('experiencia_2_fechas')
                    experiencia_2_puesto = request.form.get('experiencia_2_puesto')
                    experiencia_2_labor_1 = request.form.get('experiencia_2_labor_1')
                    experiencia_2_labor_2 = request.form.get('experiencia_2_labor_2')
                    experiencia_2_labor_3 = request.form.get('experiencia_2_labor_3')

                    cursor.execute('SELECT id_experiencia FROM experiencia WHERE id_curriculum = %s', (id_curriculum,))
                    id_experiencia = cursor.fetchall()[-1][0]
                    print(id_experiencia)
                    cursor.execute('UPDATE experiencia SET fechas = %s, puesto = %s, labor_1 = %s, labor_2 = %s, labor_3 = %s WHERE id_experiencia = %s', (experiencia_2_fechas, experiencia_2_puesto, experiencia_2_labor_1, experiencia_2_labor_2, experiencia_2_labor_3, id_experiencia))
                    mysql.connection.commit()
                    
                flash('Datos guardados correctamente')
                return redirect(url_for('perfil'))            
            
            return render_template('plantilla{}.html'.format(curriculum[1]), usuario = usuario, usuario_actual = usuario_actual, formulario = formulario, imagen = imagen, parametros = parametros_por_defecto_inputs)
        return render_template('plantilla{}.html'.format(curriculum[1]), usuario = usuario, usuario_actual = usuario_actual, formulario = formulario, imagen = imagen, parametros = parametros_por_defecto_inputs)
    
    except Exception as e:
        flash('Ha ocurrido un error: {}'.format(e))
        return redirect(url_for('perfil'))
    
    


@app.route('/admin')
@login_required
def admin():
    try:
        if current_user.correo != 'infocurriculum360@gmail.com':
            return(redirect(url_for('perfil')))
        
        
        cursor = mysql.connection.cursor()
        cursor.execute('SELECT id, nombre, apellidos FROM usuarios')
        usuarios_obtenidos = cursor.fetchall()
        usuarios = []
        for usuario_obtenido in usuarios_obtenidos:
            cursor.execute('SELECT id_curriculum, plantilla FROM curriculums INNER JOIN usuarios ON curriculums.id_usuario = usuarios.id WHERE usuarios.id = %s', (usuario_obtenido[0],))
            curriculums = cursor.fetchall()
            usuarios.append({'id_usuario':usuario_obtenido[0],'nombre':usuario_obtenido[1], 'apellidos':usuario_obtenido[2], 'curriculums':[]})
            
            for curriculum in curriculums:
                
                for usuario in usuarios:
                    if usuario['nombre'] == usuario_obtenido[1]:
                        usuario['curriculums'].append({'id_curriculum':curriculum[0], 'plantilla':curriculum[1]})
        print(usuarios)

        return render_template('admin.html', usuario = current_user, usuarios = usuarios)
    except Exception as e:
        flash('Ha ocurrido un error: {}'.format(e))
        return render_template('perfil.html', usuario = current_user, usuarios = usuarios)

@app.route('/admin/usuarios')
@login_required
def admin_usuarios():
    try:
        if current_user.correo == 'infocurriculum360@gmail.com':
            cursor = mysql.connection.cursor()
            cursor.execute('SELECT * FROM usuarios')
            usuarios = cursor.fetchall()

            return(render_template('admin_usuarios.html', usuarios = usuarios))
        return redirect(url_for(perfil))
    except Exception as e:
        flash('Ha ocurrido un error: {}'.format(e))
        return(render_template('admin_usuarios.html', usuarios = usuarios))

@app.route('/eliminar_usuario/<id>')
@login_required
def eliminar_usuario(id):
    try:
        cursor = mysql.connection.cursor()
        cursor.execute('DELETE FROM usuarios WHERE id = %s', (id,))
        mysql.connection.commit()
        return(redirect(url_for('admin')))
    except:
        flash('Ha ocurrido un error')
        return (redirect(url_for('admin_usuarios')))

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

def status_401(error):
    if current_user.is_authenticated:
        volver = '/perfil'
    else:
        volver = '/'
    
    return render_template('error_401.html', boton_volver = volver)

def status_404(error):
    if current_user.is_authenticated:
        volver = '/perfil'
    else:
        volver = '/'
    
    return render_template('error_404.html', boton_volver = volver)

if __name__ == '__main__':
    app.register_error_handler(401, status_401)
    app.register_error_handler(404, status_404)
    app.run(debug = True)