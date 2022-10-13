import json
import urllib.request

from flask import Flask, render_template

app = Flask(__name__)


# --- definicion de rutas ---

# inicio de sesion
@app.route("/")
@app.route("/login")
def mostrar_login():
    return render_template("login.html")

# registro
@app.route("/registrarse")
def mostrar_registro():
    return render_template("registro.html")

# --- dashboard ---
@app.route("/dashboard")
def mostrar_dashboard():
    return render_template("dashboard.html")

# --- trivia ---
@app.route("/trivia")
def mostrar_trivia():
    preguntas_API = obtener_preguntas(1)
    #print(preguntas_API)
    return render_template("trivia.html", preguntas=preguntas_API)

# buscar amigos
@app.route("/buscaramigos")
def mostrar_amigos():
    return render_template("buscaramigos.html")

# perfil
@app.route("/perfil")
def mostrar_perfil():
    return render_template("perfil.html")

# ranking
@app.route("/ranking")
def mostrar_ranking():
    return render_template("ranking.html")

# configuracion de administrador
@app.route("/config")
def mostrar_config():
    return render_template("config.html")

# --- API de preguntas ---
def obtener_preguntas(nivel):
    url = "http://ec2-44-203-35-246.compute-1.amazonaws.com/preguntas.php?nivel={}&grupo={}".format(nivel, 2)
    response = urllib.request.urlopen(url)
    data = response.read()
    dict = json.loads(data)
    return dict
