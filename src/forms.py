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

class Curriculum(FlaskForm):
    direccion = StringField('Introduce tu dirección', validators = [
        DataRequired(),
        Length(max=100)
    ])

    telefono = StringField('Introduce tu teléfono', validators = [
        DataRequired(),
        Length(min=9, max=9)
    ])
    resumen_profesional = TextAreaField('RESUMEN PROFESIONAL', default="Gestor experimentado con excelentes aptitudes de gestión de clientes y proyectos. Orientado a la acción con gran capacidad para comunicarse de forma eficaz con público del sector tecnológico, ejecutivo y empresarial.", validators = [
        DataRequired(),
        Length(max=255)
    ])
    Aptitud_1 = TextAreaField('', default="Gerente de compras titulado", validators = [
        DataRequired(),
        Length(min=10, max=40)
    ])
    Aptitud_2 = TextAreaField('', default="Actitud de trabajo activa", validators = [
        DataRequired(),
        Length(min=10, max=40)
    ])
    Aptitud_3 = TextAreaField('', default="Actualización de sistemas",validators = [
        DataRequired(),
        Length(min=10, max=40)
    ])
    Aptitud_4 = TextAreaField('', default="Acompañamiento de confianza",validators = [
        Length(max=40)
    ])
    Aptitud_5 = TextAreaField('', default="Supervisión del sitio comercial",validators = [
        Length(max=40)
    ])

    experiencia_1_fechas = StringField('', validators = [
        Length(max=50)
    ])
    experiencia_1_puesto = StringField('', validators = [
        Length(max=100)
    ])
    experiencia_1_labor_1 = TextAreaField('', default="Dirigí las iniciativas de desarrollo de contratación/formación/empleados para aumentar al máximo la productividad y el potencial de los ingresos a través del desarrollo de un equipo comercial.",validators = [
        Length(max=255)
    ])
    experiencia_1_labor_2 = TextAreaField('', default="Planifiqué y ejecuté iniciativas de expositores promocionales en colaboración con el departamento de administración de promociones.",validators = [
        Length(max=255)
    ])
    experiencia_1_labor_3 = TextAreaField('', default="Me ocupé de que el establecimiento estuviera preparado para someterse a auditorías internas mediante el análisis o la preparación de controles de calidad y de estadísticas de inventario.", validators = [
        Length(max=255)
    ])

    experiencia_2_fechas = StringField('', validators = [
        Length(max=50)
    ])
    experiencia_2_puesto = StringField('', validators = [
        Length(max=100)
    ])
    experiencia_2_labor_1 = TextAreaField('', default="Supervisé las operaciones de apertura y cierre de un establecimiento con ingresos anuales de 4 millones de euros en cumplimiento con las políticas y procedimientos actuales de la empresa.", validators = [
        Length(max=255)
    ])
    experiencia_2_labor_2 = TextAreaField('', default="Gestioné los costes operativos encabezando el control de inventario y liderando las actividades del departamento de envío además de fijar las nóminas.", validators = [
        Length(max=255)
    ])
    experiencia_2_labor_3 = TextAreaField('', default="Administré los procesos financieros, incluidas las cuentas a pagar y las cuentas por cobrar mediante la gestión de una oficina de contabilidad y la actualización de los archivos del servicio de atención al cliente.", validators = [
        Length(max=255)
    ])

    formacion_año = StringField('', validators=[
        Length(min=4,max=4)
    ])
    formacion_titulo = StringField('', validators=[
        Length(max=100)
    ])
    formacion_lugar = StringField('', validators=[
        Length(max=255)
    ])
    formacion_temas = TextAreaField('', default="Administración de operaciones\nUniversidad Complutense, Madrid\nTemas abordados durante el curso: oratoria y comunicación, sociología y psicología.", validators=[
        Length(max=255)
    ])

    otros = TextAreaField('', validators=[
        Length(max=255)
    ])

    finalizar = SubmitField('Finalizar')