from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, EmailField, TextAreaField
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