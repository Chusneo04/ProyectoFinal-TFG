from flask import Flask, render_template
from flask_login import current_user
from app import create_app

app = create_app()

@app.route('/')
def index():
    return render_template('index.html')

@app.errorhandler(401)
def status_401(error):
    return render_template('error_401.html', boton_volver='/perfil' if current_user.is_authenticated else '/')

@app.errorhandler(404)
def status_404(error):
    return render_template('error_404.html', boton_volver='/perfil' if current_user.is_authenticated else '/')

if __name__ == "__main__":
    app.run(debug=True)

