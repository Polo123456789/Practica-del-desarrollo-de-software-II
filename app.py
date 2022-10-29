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

@app.route('/login')
def Login():
    return render_template("Login.html")

@app.route('/perfil')
def Perfil():
    DATETIME_STRING_FORMAT = "%d/%m/%Y %H:%M:%S"
    user = {
            "nombres": "Usuario",
            "apellidos": "anonimo",
            "correo": "email@example.com",
            "idUser":  12345,
            "puntuacion":  0,
            "fechaNacimiento": "2002-11-09",
            "intentosFallidos": 0,
            "nivel": 0,
            "avatar":  "/static/img/avatars/standar.gif"}
    return render_template("Perfil.html", usuario=user)

@app.route('/administrador')
def Admin():
    return render_template("Administrador.html")




if __name__ == '__main__':
    app.run(debug = True, port= 8000)
