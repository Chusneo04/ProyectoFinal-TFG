from flask import Flask, render_template
from flask_login import current_user
from app import create_app

app = create_app()



if __name__ == "__main__":
    app.run(debug=True)

