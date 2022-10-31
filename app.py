import json
import urllib.request
import sys

from flask import Flask, session, render_template, request, jsonify, redirect, url_for, flash, g
from flask_sqlalchemy import SQLAlchemy
from datetime import date, datetime, timedelta

from functools import wraps

app = Flask(__name__)
app.secret_key = "Un valor que cambiaremos cuando vayamos a produccion "

db = SQLAlchemy()
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///db.sqlite"
app.config['PERMANENT_SESSION_LIFETIME'] =  timedelta(hours=8)
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

    invitacionesRecibidas = db.relationship("Friendship", foreign_keys='Friendship.idReceptor', back_populates="receptor")
    invitacionesEnviadas = db.relationship("Friendship", foreign_keys='Friendship.idRemitente', back_populates="remitente")

    
class Friendship(db.Model):
    # __tablename__ = 'friendship'
    idRemitente = db.Column(db.Integer(), db.ForeignKey('user.idUser'), primary_key=True)
    idReceptor = db.Column(db.Integer(), db.ForeignKey('user.idUser'), primary_key=True)
    estadoSolicitud = db.Column(db.Boolean())
    creacion = db.Column(db.DateTime())
    remitente = db.relationship("User", foreign_keys=[idRemitente], back_populates="invitacionesEnviadas")
    receptor = db.relationship("User", foreign_keys=[idReceptor], back_populates="invitacionesRecibidas")


class Cache(db.Model):
    #__tablename__ = 'cache'
    idPregunta = db.Column(db.Integer(), primary_key=True)
    pregunta = db.Column(db.String(), nullable=False, unique=False)    
    opcion1 = db.Column(db.String(), nullable=False, unique=False)
    opcion2 = db.Column(db.String(), nullable=False, unique=False)
    opcion2 = db.Column(db.String(), nullable=False, unique=False)
    opCorrecta = db.Column(db.String(), nullable=False, unique=False)


DATE_STRING_FORMAT = "%Y-%m-%d"
DATETIME_STRING_FORMAT = "%d/%m/%Y %H:%M:%S"
POINTS_PER_LEVEL = 25
POINTS_PER_GOOD_ANSWER = 5
DAYS_TO_GET_SAD = 7


def updateLevelAndGetProgress(user):
    user.nivel = (user.puntuacion // POINTS_PER_LEVEL) + 1
    currentPoints = user.puntuacion % POINTS_PER_LEVEL
    return (currentPoints / POINTS_PER_LEVEL) * 100


def getCurrentQuestionNo(user):
    return 1 + (user.puntuacion // POINTS_PER_GOOD_ANSWER)


def requires_login(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        if not "user" in session:
            flash("Tiene que iniciar sesion primero")
            return redirect(url_for("mostrar_login"))
        else:
            return fn(*args, **kwargs)

    return wrapper


def get_user() -> User:
    return User.query.filter_by(email=session["user"]).first()


# --- definicion de rutas ---

# inicio de sesion
@app.route("/")
def index():
    return redirect(url_for("mostrar_login"))


@app.route("/login", methods=['GET', 'POST'])
def mostrar_login():
    if request.method == 'POST':
        form = request.form
        email = form["correo"]
        contraseña = form["contraseña"]
        
        usuario = User.query.filter_by(email=email, contraseña=contraseña).first()

        if usuario:
            session["user"] = usuario.email
            session.permanent = True

            ultima = usuario.ultimaParticipacion
            hoy = date.today()
            ayer = hoy - timedelta(1)
            if ayer == ultima:
                usuario.racha += 1
            else:
                usuario.racha = 1
            usuario.ultimaParticipacion = hoy

            db.session.commit()

            if usuario.administrador == 1:
                return redirect(url_for('rankingAdmin'))
            else:
                return redirect(url_for('dashboard'))
        else:
            flash("Correo o contraseña incorrectos");
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

        return redirect(url_for('mostrar_login'))

    return render_template('Registro.html')


@app.route("/dashboard")
@requires_login
def dashboard():
    user = get_user()
    today = date.today()
    avatarVariant = "normal"

    
    delta = today - user.ultimaParticipacion
    if delta.days >= 7:
        avatarVariant = "sad"

    progress = updateLevelAndGetProgress(user)
    db.session.commit()

    return render_template("Dashboard.html",
                           usuario=user,
                           progress=progress,
                           avatarVariant=avatarVariant)


# --- trivia ---
@app.route("/trivia", methods=['GET', 'POST'])
@requires_login
def mostrar_trivia():
    if request.method == 'GET':
        user = get_user()
        noPregunta = getCurrentQuestionNo(user)
        pregunta = obtener_preguntas(noPregunta)
        progress = updateLevelAndGetProgress(user)
        db.session.commit()
        return render_template("Trivia.html",
                               usuario=user,
                               progress=progress,
                               pregunta=pregunta)
    else:
        user = get_user()
        correct = request.json['correct']
        if correct:
            user.puntuacion += POINTS_PER_GOOD_ANSWER
        else:
            user.intentosFallidos += 1
        db.session.commit()
        return jsonify({"msg": "Actualizado correctamente"})


# buscar amigos
@app.route("/buscar-amigos")
@requires_login
def mostrar_amigos():
    return render_template("buscaramigos.html")


# perfil
@app.route("/perfil", methods=["GET", "POST"])
@requires_login
def mostrar_perfil():
    if request.method == "GET":
        user = get_user()
        return render_template("perfil.html", usuario=user)
    else:
        form = request.form
        user: User = get_user()

        user.nombres = form["nombres"]
        user.apellidos = form["apellidos"]
        user.fechaNacimiento = date.fromisoformat(form["nac"])
        user.email = form["correo"]

        if form["contraseña"] != "":
            user.contraseña = form["contraseña"]

        if "activarCorreos" in form:
            user.activarCorreos = True
        else:
            user.activarCorreos = False

        user.avatar = form["avatar"]

        db.session.commit()

        return redirect(url_for("dashboard"))


# ranking Admin
@app.route("/rankingAdmin")
@requires_login
def mostrar_rankingAdmin():
    mayor = User.query.order_by(User.puntuacion.desc(), User.intentosFallidos.asc()).limit(10).all
    menor = User.query.order_by(User.puntuacion.asc(), User.intentosFallidos.desc()).limit(10).all
    return render_template("ranking.html")


# ranking
@app.route("/ranking")
@requires_login
def mostrar_ranking():
    return render_template("ranking.html")


# configuracion de administrador
@app.route("/config")
@requires_login
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