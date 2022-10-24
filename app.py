from flask import Flask
from flask import render_template

app = Flask(__name__)

@app.route('/dashboard')
def Dashboard():
    return render_template("Dashboard.html")

@app.route('/trivia')
def Trivia():
    return render_template("Trivia.html")

@app.route('/registro')
def Registro():
    return render_template("Registro.html")

if __name__ == '__main__':
    app.run(debug = True, port= 8000)
