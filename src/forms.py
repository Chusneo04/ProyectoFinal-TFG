from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, EmailField
from wtforms.validators import DataRequired, Email, Length, EqualTo, ValidationError

class Usuario(FlaskForm):
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