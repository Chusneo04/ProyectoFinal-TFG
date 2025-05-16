from flask import Flask, redirect, render_template, request, url_for, flash
import os
from flask_mysqldb import MySQL
from datetime import datetime
from dotenv import load_dotenv
from forms import Usuario_register, Usuario_login, Recuperar_clave_email, Nueva_Clave, Editar_perfil, Editar_clave, Clave_nueva, Contacto, Curriculum
from werkzeug.security import generate_password_hash, check_password_hash
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

        if usuario.validate_on_submit() and request.method == 'POST':

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
            cursor = mysql.connection.cursor()
            cursor.execute('UPDATE usuarios SET nombre = %s, apellidos = %s, correo = %s WHERE id = %s', (nombre, apellidos, correo, id))
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
        curriculum = Curriculum()
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



                return render_template('plantilla{}.html'.format(plantilla), curriculum_id = id, usuario = current_user, imagen = imagen, formulario = curriculum)
            return render_template('plantilla{}.html'.format(plantilla), curriculum_id = id, usuario = current_user, imagen = imagen, formulario = curriculum)
        return redirect(url_for('elegir_plantilla'))
    except Exception as e:
        print('Error: {}'.format(e))
        return render_template('plantilla{}.html'.format(plantilla), curriculum_id = id, usuario = current_user, imagen = imagen, formulario = curriculum)

@app.route('/eliminar_curriculum/<id_curriculum>')
@login_required
def eliminar_curriculum(id_curriculum):
    try:
        cursor = mysql.connection.cursor()
        cursor.execute('SELECT id_usuario FROM curriculums WHERE id_curriculum = %s', (id_curriculum,))
        id_usuario = cursor.fetchone()
        if id_usuario == current_user.id:
            cursor.execute('DELETE FROM curriculums WHERE id_curriculum = %s', (id_curriculum,))
            mysql.connection.commit()
            return redirect(url_for('perfil'))
        flash('No puedes eliminar curriculums que no son tuyos.')
        return redirect(url_for('perfil'))
    except Exception as e:
        flash(e)
        return redirect(url_for('perfil'))


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)