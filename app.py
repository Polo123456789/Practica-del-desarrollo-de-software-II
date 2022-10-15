import json
import urllib.request
import sys

from flask import Flask, session, render_template
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.secret_key = "Un valor que cambiaremos cuando vayamos a produccion "

db = SQLAlchemy()
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///db.sqlite"
db.init_app(app)

class User(db.Model):
    #__tablename__ = 'users'
    idUser = db.Column(db.Integer(), primary_key=True)
    nombres = db.Column(db.String(30), nullable=False, unique=False)
    apellidos = db.Column(db.String(30), nullable=False, unique=False)
    fechaNacimiento = db.Column(db.Date(), nullable=False, unique=False)
    email = db.Column(db.String(50), nullable=False, unique=True)
    contraseña = db.Column(db.String(12), nullable=False, unique=True) # Contraseñas unicas? 12 caracteres para el hash?
    activarCorreos = db.Column(db.Boolean(), nullable=False, unique=False)
    puntuacion = db.Column(db.Integer(), nullable=False, unique=False)
    nivel = db.Column(db.Integer(), nullable=False, unique=False)
    intentosFallidos = db.Column(db.Integer(), nullable=False, unique=False)
    avatar = db.Column(db.String(), nullable=False, unique=False)
    racha = db.Column(db.Integer(), nullable=False, unique=False)
    ultimaParticipacion = db.Column(db.Date(), nullable=False, unique=False)

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
            "nombres": "Usuario",
            "apellidos": "anonimo",
            "idUser":  12345,
            "nivel":  7,
            "puntuacion":  70,
            "intentosFallidos": 5,
            "avatar":  "/static/img/to-be-determined.gif",
            "lastLogin":  now.strftime(DATETIME_STRING_FORMAT),
        }

    lastLogin = datetime.strptime(session["user"]["lastLogin"],
                                  DATETIME_STRING_FORMAT)
    
    timePast = now - lastLogin
    tenMinutes = 60 * 10

    if timePast.total_seconds() > tenMinutes:
        session["user"]["avatar"] = "/static/img/to-be-determined-sad.gif"

    session["user"]["lastLogin"] = now.strftime(DATETIME_STRING_FORMAT)

    
    return render_template("Dashboard.html", usuario=session["user"])

# --- trivia ---
@app.route("/trivia")
def mostrar_trivia():
    pregunta = obtener_preguntas(1)
    print(pregunta)
    return render_template("Trivia.html",
                           usuario=session["user"],
                           pregunta=pregunta)

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

# Unicamente como una utilidad ahora en el desarrollo
@app.route("/clear-session")
def limpiar_session():
    session.clear()
    return "Listo"

# --- API de preguntas ---
def obtener_preguntas(nivel):
    url = "http://ec2-44-203-35-246.compute-1.amazonaws.com/preguntas.php?nivel={}&grupo={}".format(nivel, 2)
    response = urllib.request.urlopen(url)
    data = response.read()
    dict = json.loads(data)
    return dict


if __name__ == "__main__":
    if len(sys.argv) == 2 and sys.argv[1] == "--create-db":
        with app.app_context():
            db.create_all()
    else:
        app.run(debug=True)
