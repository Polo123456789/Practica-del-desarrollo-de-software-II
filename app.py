import json
from string import punctuation
import urllib.request
import sys

from flask import Flask, session, render_template, request, jsonify, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, date

from flask_session import Session

app = Flask(__name__)
app.secret_key = "Un valor que cambiaremos cuando vayamos a produccion "

app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)


db = SQLAlchemy()
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///db.sqlite"
db.init_app(app)

class User(db.Model):
    #__tablename__ = 'users'
    idUser = db.Column(db.Integer(), primary_key=True, autoincrement=True)
    nombres = db.Column(db.String(30), nullable=False, unique=False)
    apellidos = db.Column(db.String(30), nullable=False, unique=False)
    fechaNacimiento = db.Column(db.Date(), nullable=False, unique=False)
    email = db.Column(db.String(50), nullable=False, unique=True)
    contraseña = db.Column(db.String(12), nullable=False) # Contraseñas unicas? 12 caracteres para el hash?
    activarCorreos = db.Column(db.Boolean(), nullable=False, unique=False)
    puntuacion = db.Column(db.Integer(), nullable=False, unique=False)
    nivel = db.Column(db.Integer(), nullable=False, unique=False)
    intentosFallidos = db.Column(db.Integer(), nullable=False, unique=False)
    avatar = db.Column(db.String(), nullable=False, unique=False)
    racha = db.Column(db.Integer(), nullable=False, unique=False)
    ultimaParticipacion = db.Column(db.Date(), nullable=False, unique=False)


DATETIME_STRING_FORMAT = "%d/%m/%Y %H:%M:%S"
POINTS_PER_LEVEL = 25
POINTS_PER_GOOD_ANSWER = 5

def updateLevelAndGetProgress(user):
    user["nivel"] = (user["puntuacion"] // POINTS_PER_LEVEL) + 1
    currentPoints = user["puntuacion"] % POINTS_PER_LEVEL
    return (currentPoints / POINTS_PER_LEVEL) * 100

def getCurrentQuestionNo(user):
    return 1 + (user['puntuacion'] // POINTS_PER_GOOD_ANSWER)

# --- definicion de rutas ---

# inicio de sesion
@app.route("/")
@app.route("/login", methods=['GET', 'POST'])
def mostrar_login():
    if request.method == 'POST':
        form = request.form
        nombres = form["nombres"]
        contraseña = form["contraseña"]
        user = db.session.execute(db.select(User).filter_by(nombres=nombres)).one()
        session["nombres"] = nombres
        if user:
            return redirect(url_for('dashboard'), usuario=user)
        else:
            return render_template("login.html")
    else:
        return render_template("login.html")

# registro
@app.route("/registro", methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        form = request.form
        nombres = form["nombres"]
        apellidos = form["apellidos"]
        nac = form["nac"] #str type
        nac_date = datetime.strptime(nac, "%m/%d/%Y")
        email = form["correo"]
        contraseña = form["contraseña"]
        avatar = form["avatar"]
        now = datetime.now()
        user = User(
            nombres = nombres,
            apellidos =apellidos,
            fechaNacimiento = nac_date,
            activarCorreos = False,
            puntuacion = 0,
            nivel = 0,
            intentosFallidos = 0,
            avatar = avatar,
            racha = 0,
            ultimaParticipacion = now.strftime(DATETIME_STRING_FORMAT)
        )
        buscar_usuario = False#db.session.execute(db.select(User).filter_by(nombres=nombres)).one()
        if buscar_usuario:
            return render_template('registro.html', form=form)
        else:
            db.session.add(user)
            db.session.commit()
            return redirect(url_for('dashboard'), usuario=user)
    print("registration fail")
    return render_template('registro.html')


@app.route("/dashboard")
def dashboard():
    now = datetime.now()

    # Le daremos unos valores default a las sesiones en lo que implementamos
    # los usuarios la proxima semana
    if not "user" in session:
        session["user"] = {
            "nombres": "Usuario",
            "apellidos": "anonimo",
            "idUser": 12345,
            "puntuacion": 0,
            "intentosFallidos": 0,
            "nivel": 0,
            "avatar": "/static/img/avatars/standar.gif",
            "lastLogin": now.strftime(DATETIME_STRING_FORMAT),
        }

    lastLogin = datetime.strptime(session["user"]["lastLogin"],
                                  DATETIME_STRING_FORMAT)

    timePast = now - lastLogin
    timeToGetSadInSeconds = 3

    if timePast.total_seconds() > timeToGetSadInSeconds:
        session["user"]["avatar"] = "/static/img/avatars/sad.gif"
    else:
        session['user']['avatar'] = '/static/img/avatars/standar.gif'

    session["user"]["lastLogin"] = now.strftime(DATETIME_STRING_FORMAT)

    progress = updateLevelAndGetProgress(session["user"])

    session.modified = True

    return render_template("Dashboard.html",
                           usuario=session["user"],
                           progress=progress)

# --- trivia ---
@app.route("/trivia", methods=['GET', 'POST'])
def mostrar_trivia():
    if request.method == 'GET':
        noPregunta = getCurrentQuestionNo(session['user'])
        pregunta = obtener_preguntas(noPregunta)
        progress = updateLevelAndGetProgress(session["user"])
        return render_template("Trivia.html",
                            usuario={**session["user"], "noPregunta": noPregunta},
                            progress=progress,
                            pregunta=pregunta)
    else:
        print(request.json)
        correct = request.json['correct']
        if correct:
            session['user']['puntuacion'] += POINTS_PER_GOOD_ANSWER
        else:
            session['user']['intentosFallidos'] += 1

        session.modified = True

        return jsonify({"msg": "Actualizado correctamente"})

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
