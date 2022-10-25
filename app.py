import json
from string import punctuation
import urllib.request
import sys

from flask import Flask, session, render_template, request, jsonify, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import date, datetime

app = Flask(__name__)
app.secret_key = "Un valor que cambiaremos cuando vayamos a produccion "

db = SQLAlchemy()
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///db.sqlite"
db.init_app(app)


class User(db.Model):
    # __tablename__ = 'users'
    idUser = db.Column(db.Integer(), primary_key=True)
    nombres = db.Column(db.String(30), nullable=False, unique=False)
    apellidos = db.Column(db.String(30), nullable=False, unique=False)
    fechaNacimiento = db.Column(db.Date(), nullable=False, unique=False)
    email = db.Column(db.String(50), nullable=False, unique=True)
    contraseña = db.Column(db.String(60), nullable=False, unique=False) 
    activarCorreos = db.Column(db.Boolean(), nullable=False, unique=False)
    puntuacion = db.Column(db.Integer(), nullable=False, unique=False)
    nivel = db.Column(db.Integer(), nullable=False, unique=False)
    intentosFallidos = db.Column(db.Integer(), nullable=False, unique=False)
    avatar = db.Column(db.Integer(), nullable=False, unique=False)
    racha = db.Column(db.Integer(), nullable=False, unique=False)
    ultimaParticipacion = db.Column(db.Date(), nullable=False, unique=False)
    administrador = db.Column(db.Boolean(), nullable=False, unique=False)

    
class Friendship(db.Model):
    # __tablename__ = 'friendship'
    idRemitente = db.Column(db.Integer(), db.ForeignKey('user.idUser'), primary_key=True)
    idReceptor = db.Column(db.Integer(), db.ForeignKey('user.idUser'), primary_key=True)
    estadoSolicitud = db.Column(db.Boolean())
    creacion = db.Column(db.DateTime())
    remitente = db.relationship("User", foreign_keys=[idRemitente], backref="invitacionesRecibidas")
    receptor = db.relationship("User", foreign_keys=[idReceptor], backref="invitacionesEnviadas")


class Cache(db.Model):
    #__tablename__ = 'cache'
    idPregunta = db.Column(db.Integer(), primary_key=True)
    pregunta = db.Column(db.String(), nullable=False, unique=False)    
    opcion1 = db.Column(db.String(), nullable=False, unique=False)
    opcion2 = db.Column(db.String(), nullable=False, unique=False)
    opcion2 = db.Column(db.String(), nullable=False, unique=False)
    opCorrecta = db.Column(db.String(), nullable=False, unique=False)


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
def index():
    return render_template("index.html")


@app.route("/login", methods=['GET', 'POST'])
def mostrar_login():
    if request.method == 'POST':
        if "user" in session:
            return redirect(url_for('dashboard'))
        else:
            form = request.form
            nombres = form["nombres"]
            contraseña = form["contraseña"]
            session["nombres"] = nombres
            buscar_usuario = db.session.execute(db.select(User).filter_by(nombres=nombres, contraseña=contraseña)).one()
            if buscar_usuario:
                return redirect(url_for('dashboard', usuario=buscar_usuario))
            else:
                return render_template("login.html", form=form)
    else:
        return render_template("login.html")


# registro
@app.route("/registro", methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        form = request.form

        nombres = form["nombres"]
        apellidos = form["apellidos"]
        nac = date.fromisoformat(form["nac"])
        email = form["correo"]
        contraseña = form["contraseña"]
        avatar = int(form["avatar"])
        participacionInicial = date.today()

        user = User(
            nombres=nombres,
            apellidos=apellidos,
            fechaNacimiento=nac,
            email=email,
            contraseña=contraseña,
            activarCorreos=True,
            puntuacion=0,
            nivel=1,
            intentosFallidos=0,
            avatar=avatar,
            racha=1,
            ultimaParticipacion=participacionInicial,
            administrador = False
        )
        db.session.add(user)
        db.session.commit()

        session["user"] = email;

        return redirect(url_for('dashboard'))

    return render_template('Registro.html')


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
    if "user" in session:
        user_email = session["email"]
        user = db.session.execute(db.select(User).filter_by(email=user_email)).one()
        return render_template("perfil.html", ususario=user)
    else:
        return redirect(url_for('login'))


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
    return redirect(url_for("mostrar_login"))


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
            User1= User(
                nombres ="Elian André", 
                apellidos = "Reyes Mox", 
                fechaNacimiento = date.today(),
                email = "administrador@gmail.com", 
                contraseña = "abc123!", 
                activarCorreos = 1, 
                puntuacion = 0, 
                nivel = 1, 
                intentosFallidos = 0, 
                avatar = 1, 
                racha = 0, 
                ultimaParticipacion = date.today(), 
                administrador = 1
            )

            db.session.add(User1)
            db.session.commit()
    else:
        app.run(debug=True)