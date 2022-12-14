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

duracionCache = timedelta(0, 5 * 60);
webServiceUrl = "http://ec2-44-203-35-246.compute-1.amazonaws.com/preguntas.php?nivel={nivel}&grupo={grupo}"
cache = {}

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
            return redirect(url_for('dashboard'))

        else:
            flash("Correo o contraseña incorrectos");
            return render_template("Login.html")
    else:
        if "user" in session:
            return redirect(url_for('dashboard'))
        return render_template("Login.html")


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

    if user.administrador:
        return redirect(url_for('mostrar_rankingAdmin'))

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


def cacheIsValid(cache) -> bool:
    delta = datetime.now() - cache["lastUpdated"]
    return delta < duracionCache



# --- trivia ---
@app.route("/trivia", methods=['GET', 'POST'])
@requires_login
def mostrar_trivia():
    global cache

    if request.method == 'GET':
        user = get_user()
        noPregunta = getCurrentQuestionNo(user)
        pregunta = None
        
        if noPregunta in cache:
            pregunta = cache[noPregunta]
            if cacheIsValid(pregunta):
                pass
            else:
                try:
                    pregunta = obtener_preguntas(noPregunta)
                    pregunta["lastUpdated"] = datetime.now()
                    cache[noPregunta] = pregunta
                except:
                    app.logger.error(f"El web service no responde, retornando pregunta {noPregunta} del cache aunque sea invalido")
        else:
            try:
                pregunta = obtener_preguntas(noPregunta)
                pregunta["lastUpdated"] = datetime.now()
                cache[noPregunta] = pregunta
            except Exception as e:
                flash('El web service no responde, y la pregunta que usted solicito'
                      + ' no se encuentra en la cache. Porfavor intentelo de nuevo'
                      + ' mas tarde, si el problema persiste comuniquese con el '
                      + 'administrador del sitio')
                app.logger.error(e)
                return redirect(url_for('dashboard'))

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
        return render_template("Perfil.html", usuario=user)
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
    usuario = get_user()
    mejores = User.query.filter_by(administrador=False)\
                        .order_by(User.puntuacion.desc(),
                                  User.intentosFallidos.asc())\
                        .limit(10)\
                        .all()
    peores = User.query.filter_by(administrador=False)\
                       .order_by(User.puntuacion.asc(),
                                 User.intentosFallidos.desc())\
                       .limit(10)\
                       .all()
    return render_template("ranking.html",
                           usuario=usuario,
                           mejores=mejores,
                           peores=peores)

# configuracion de administrador
@app.route("/config")
@requires_login
def mostrar_config():
    usuario = get_user()
    return render_template("Administrador.html",
                           usuario=usuario,
                           duracionCache=int(duracionCache.total_seconds() / 60),
                           webServiceUrl=webServiceUrl)


@app.route("/config/cache", methods=["POST"])
@requires_login
def actualizar_cache():
    global duracionCache
    minutos = int(request.form["duracionDeCache"])
    duracionCache = timedelta(0, minutos * 60)
    print(f"{minutos=}, {duracionCache=}")
    return redirect(url_for("mostrar_config"))


@app.route("/config/web_server", methods=["POST"])
@requires_login
def actualizar_web_server():
    global webServiceUrl
    webServiceUrl = request.form["web_server_url"]
    return redirect(url_for("mostrar_config"))

@app.route("/add-admin", methods=["POST"])
def agregar_administrador():
    idUser = request.form["idUser"]
    u: User = User.query.get(idUser)
    u.administrador = True
    db.session.commit()
    return redirect(url_for("mostrar_rankingAdmin"))


@app.route("/clear-session")
def limpiar_session():
    session.clear()
    return redirect(url_for("mostrar_login"))

@app.route("/cache-state")
def cache_state():
    return jsonify(cache)


# --- API de preguntas ---
def obtener_preguntas(nivel):
    url = webServiceUrl.format(nivel=nivel, grupo=2)
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