from flask_login import UserMixin

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

    def get_id(self):
        return self.id  #Flask Login usa esto para identificar al usuario
