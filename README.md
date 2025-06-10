Curriculum360

Esto es una página web que permite al usuario gestionar currículums

Funcionalidades para el Usuario:
Autenticación completa: registro, login y recuperación de contraseña por email.
Creación, edición y eliminación de currículums.
Creación de currículums a partir de plantillas prediseñadas a elección del usuario.
Edición de perfil

RUTA DE ADMINISTRADOR:

¡¡¡PARA QUE EXISTA UN USUARIO ADMINISTRADOR SE DEBE CREAR CON EL CORREO "infocurriculum360@gmail.com"!!!

El administrador puede Editar y eliminar los curriculums de cualquier usuario además de crear los suyos
Eliminar usuarios

Extras Técnicos:
Control de errores personalizado con páginas para códigos 401 y 404.
Uso de tokens para la recuperación de contraseñas.
Estructura modularizada en Flask

Requisitos
Para ejecutar este proyecto, necesitas:

Instalar los paquetes que contiene el requeriments.txt

Clona el repositorio

Ejecuta el siguiente comando en tu terminal:
https://github.com/Chusneo04/ProyectoFinal-TFG.git
cd ProyectoFinal-TFG
Crear entorno virtual:
python -m venv env
source env/bin/activate (esto en linux y apple)
env\Scripts\activate    (Esto en windows)
Instala las dependencias
pip install -r requeriments.txt

Ejectua la aplicacion
 python src/app.py 
Acceder en el navegador a http://127.0.0.1:5000
