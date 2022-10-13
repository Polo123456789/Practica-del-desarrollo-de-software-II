import json
import urllib.request

from flask import Flask, session, render_template
from datetime import datetime

app = Flask(__name__)
app.secret_key = "Un valor que cambiaremos cuando vayamos a produccion "

DATETIME_STRING_FORMAT = "%d/%m/%Y %M:%H:%S"

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

@app.route("/dashboard")
def dashboard():
    now = datetime.now()

    # Le daremos unos valores default a las sesiones en lo que implementamos
    # los usuarios la proxima semana
    if not "user" in session:
        session["user"] = {
            "nombreUsuario": "Usuario anonimo",
            "id":  12345,
            "nivel":  7,
            "puntuacion":  70,
            "avatar":  "/static/img/to-be-determined.gif",
            "lastLogin":  now.strftime(DATETIME_STRING_FORMAT),
        }

    lastLogin = datetime.strptime(session["user"]["lastLogin"],
                                  DATETIME_STRING_FORMAT)
    
    timePast = now - lastLogin
    tenMinutes = 60 * 10

    if timePast.total_seconds() > tenMinutes:
        session["user"]["avatar"] = "/static/img/to-be-determined-sad.gif"
    

    # Pendiente de tener el template para rellenarlo
    return json.dumps(session["user"])

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


if __name__ == "__main__":
    app.run()