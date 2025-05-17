from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, EmailField, TextAreaField, IntegerField
from wtforms.validators import DataRequired, Email, Length, EqualTo, ValidationError

class Usuario_register(FlaskForm):
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

    clave = PasswordField('Clave', validators=[
        DataRequired(),
        Length(min=8, max=255),
        EqualTo('confirmar_clave', message='La confirmación debe coincidir con la clave')
    ])

    confirmar_clave = PasswordField('Confirmar clave', validators=[
        DataRequired(),
        Length(min=8, max=255)
    ])

    registrar = SubmitField('Registrar')

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

class Recuperar_clave_email(FlaskForm):
    correo = EmailField('Correo', validators=[
        DataRequired(),
        Length(max=100),
        Email()
    ])

    enviar = SubmitField('Enviar')

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

    guardar = SubmitField('Guardar')

class Editar_clave(FlaskForm):
    contraseña = PasswordField('Contraseña actual', validators=[
        DataRequired(),
        Length(min=8, max=255),
    ])

    siguiente = SubmitField('Siguiente')

class Clave_nueva(FlaskForm):
    contraseña = PasswordField('Nueva contraseña', validators = [
        DataRequired(),
        Length(min=8, max=255),
    ])

    actualizar = SubmitField('Actualizar contraseña')

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

    experiencia_1_fechas = StringField('', validators = [
        Length(max=50)
    ])
    experiencia_1_puesto = StringField('', validators = [
        Length(max=100)
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

    experiencia_2_fechas = StringField('', validators = [
        Length(max=50)
    ])
    experiencia_2_puesto = StringField('', validators = [
        Length(max=100)
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

    formacion_1_año = StringField('', validators=[
        Length(min=4,max=5)
    ])
    formacion_1_titulo = StringField('', validators=[
        Length(max=100)
    ])
    formacion_1_temas = TextAreaField('', validators=[
        Length(max=255)
    ])

    formacion_2_año = StringField('', validators=[
        Length(min=4,max=4)
    ])
    formacion_2_titulo = StringField('', validators=[
        Length(max=100)
    ])
    formacion_2_temas = TextAreaField('', validators=[
        Length(max=255)
    ])

    finalizar = SubmitField('Finalizar y Guardar')