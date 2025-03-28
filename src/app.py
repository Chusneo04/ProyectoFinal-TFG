from flask import Flask, redirect, render_template, url_for

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')
    

if __name__ == '__main__':
    app.run(debug=True, host="172.31.52.67", port=5500)