from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, EmailField, TextAreaField, FileField
from wtforms.validators import DataRequired, Email, Length, EqualTo, ValidationError

# Definimos el formulario para registrar un nuevo usuario
class Usuario_register(FlaskForm):
    nombre = StringField('Nombre', validators=[
        DataRequired(),
        Length(max=30)
    ])

    # Campo para los apellidos
    apellidos = StringField('Apellidos', validators=[
        DataRequired(),
        Length(max=80)
    ])

    # Campo para el correo electrónico con validación de formato
    correo = EmailField('Correo', validators=[
        DataRequired(),
        Length(max=100),
        Email()
    ])

    # Campo para la contraseña con validación de coincidencia con confirmación
    clave = PasswordField('Clave', validators=[
        DataRequired(),
        Length(min=8, max=255),
        EqualTo('confirmar_clave', message='La confirmación debe coincidir con la clave')
    ])

    # Campo para confirmar la contraseña
    confirmar_clave = PasswordField('Confirmar clave', validators=[
        DataRequired(),
        Length(min=8, max=255)
    ])

    # Botón para enviar el formulario
    registrar = SubmitField('Registrar')

# Definimos el formulario para iniciar sesión
class Usuario_login(FlaskForm):
    correo = EmailField('Correo', validators=[
        DataRequired(),
        Length(max=100),
        Email()
    ])

    clave = PasswordField('Clave', validators=[
        DataRequired()
    ])

    iniciar_sesion = SubmitField('Iniciar sesión')

# Formulario para recuperar la contraseña mediante correo electrónico
class Recuperar_clave_email(FlaskForm):
    correo = EmailField('Correo', validators=[
        DataRequired(),
        Length(max=100),
        Email()
    ])

    enviar = SubmitField('Enviar')

# Formulario para introducir una nueva contraseña
class Nueva_Clave(FlaskForm):
    contraseña = PasswordField('Nueva Contraseña', validators=[
        DataRequired(),
        Length(min=8, max=255),
        EqualTo('confirmar_clave', message='La confirmación debe coincidir con la clave')
    ])

    confirmar_clave = PasswordField('Confirmar contraseña', validators=[
        DataRequired(),
        Length(min=8, max=255)
    ])

    enviar = SubmitField('Enviar')

# Formulario para editar el perfil del usuario
class Editar_perfil(FlaskForm):
    nombre = StringField('Nombre', validators=[
        DataRequired(),
        Length(max=30)
    ])

    apellidos = StringField('Apellidos', validators=[
        DataRequired(),
        Length(max=80)
    ])

    correo = EmailField('Correo', validators=[
        DataRequired(),
        Length(max=100),
        Email()
    ])
    
    # Campo para subir una imagen de perfil
    imagen = FileField('Selecciona una imagen')

    guardar = SubmitField('Guardar')

# Formulario para introducir la contraseña actual antes de cambiarla
class Editar_clave(FlaskForm):
    contraseña = PasswordField('Contraseña actual', validators=[
        DataRequired(),
        Length(min=8, max=255),
    ])

    siguiente = SubmitField('Siguiente')

# Formulario para establecer una nueva contraseña
class Clave_nueva(FlaskForm):
    contraseña = PasswordField('Nueva contraseña', validators = [
        DataRequired(),
        Length(min=8, max=255),
    ])

    actualizar = SubmitField('Actualizar contraseña')

# Formulario de contacto general
class Contacto(FlaskForm):
    nombre = StringField('Nombre', validators=[
        DataRequired(),
        Length(max=30)
    ])

    correo = EmailField('Correo', validators=[
        DataRequired(),
        Length(max=100),
        Email()
    ])

    mensaje = TextAreaField('Mensaje', validators=[
        DataRequired()
    ])

    enviar = SubmitField('Enviar')

# Formulario para introducir información en un CV
class Curriculum(FlaskForm):
    direccion = StringField('Introduce tu dirección', validators = [
        DataRequired(),
        Length(max=100)
    ])

    telefono = StringField('Introduce tu teléfono', validators = [
        DataRequired(),
        Length(min=9, max=9)
    ])
    
    resumen_profesional = TextAreaField('RESUMEN PROFESIONAL', validators = [
        DataRequired(),
        Length(max=255)
    ])

    # Campos para introducir aptitudes del usuario
    Aptitud_1 = TextAreaField('', validators = [
        DataRequired(),
        Length(min=10, max=40)
    ])
    Aptitud_2 = TextAreaField('', validators = [
        DataRequired(),
        Length(min=10, max=40)
    ])
    Aptitud_3 = TextAreaField('',validators = [
        DataRequired(),
        Length(min=10, max=40)
    ])
    Aptitud_4 = TextAreaField('',validators = [
        Length(max=40)
    ])
    Aptitud_5 = TextAreaField('',validators = [
        Length(max=40)
    ])

    # Experiencia laboral 1
    experiencia_1_fechas = StringField('', validators = [
        Length(max=40)
    ])
    experiencia_1_puesto = StringField('', validators = [
        Length(max=40)
    ])
    experiencia_1_labor_1 = TextAreaField('',validators = [
        Length(max=255)
    ])
    experiencia_1_labor_2 = TextAreaField('',validators = [
        Length(max=255)
    ])
    experiencia_1_labor_3 = TextAreaField('', validators = [
        Length(max=255)
    ])

    # Experiencia laboral 2
    experiencia_2_fechas = StringField('', validators = [
        Length(max=40)
    ])
    experiencia_2_puesto = StringField('', validators = [
        Length(max=40)
    ])
    experiencia_2_labor_1 = TextAreaField('', validators = [
        Length(max=255)
    ])
    experiencia_2_labor_2 = TextAreaField('', validators = [
        Length(max=255)
    ])
    experiencia_2_labor_3 = TextAreaField('', validators = [
        Length(max=255)
    ])

    # Formación académica 1
    formacion_1_año = StringField('', validators=[
        Length(min=4,max=5)
    ])
    formacion_1_titulo = StringField('', validators=[
        Length(max=40)
    ])
    formacion_1_temas = TextAreaField('', validators=[
        Length(max=255)
    ])

    # Formación académica 2
    formacion_2_año = StringField('', validators=[
        Length(min=4,max=4)
    ])
    formacion_2_titulo = StringField('', validators=[
        Length(max=40)
    ])
    formacion_2_temas = TextAreaField('', validators=[
        Length(max=255)
    ])

    # Botón para finalizar y guardar el currículum
    finalizar = SubmitField('Finalizar y Guardar')
