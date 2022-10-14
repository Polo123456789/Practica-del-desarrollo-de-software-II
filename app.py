from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Table
from db import Base
from sqlalchemy.orm import relationship

# create the extension
db = SQLAlchemy()
# create the app
app = Flask(__name__)
# configure the SQLite database, relative to the app instance folder
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///project.db"
# initialize the app with the extension
db.init_app(app)


friendship = Table(
    'friendships', Base.metadata,
    db.Column('friend_a_id', db.Integer, db.ForeignKey('users.idUser'), 
                                        primary_key=True),
    db.Column('friend_b_id', db.Integer, db.ForeignKey('users.idUser'), 
                                        primary_key=True)
)

class User(Base):
    __tablename__ = 'users'
    idUser = db.Column(db.Integer(), primary_key=True)
    nombres = db.Column(db.String(30), nullable=False, unique=False)
    apellidos = db.Column(db.String(30), nullable=False, unique=False)
    fechaNacimiento = db.Column(db.Date(), nullable=False, unique=False)
    email = db.Column(db.String(50), nullable=False, unique=True)
    contraseña = db.Column(db.String(12), nullable=False, unique=True)
    activarCorreos = db.Column(db.Boolean(), nullable=False, unique=False)
    puntuacion = db.Column(db.Integer(), nullable=False, unique=False)
    nivel = db.Column(db.Integer(), nullable=False, unique=False)
    intentosFallidos = db.Column(db.Integer(), nullable=False, unique=False)
    avatar = db.Column(db.String(), nullable=False, unique=False)
    racha = db.Column(db.Integer(), nullable=False, unique=False)
    ultimaParticipacion = db.Column(db.Date(), nullable=False, unique=False)
    solicitudesRecibidas = relationship("User", secondary=friendship, 
                           primaryjoin=id==friendship.c.friend_a_id,)
    solicitudesEnviadas = relationship("User", secondary=friendship, 
                           primaryjoin=id==friendship.c.friend_b_id,)


class Friend(Base):
    __tablename__ = 'friends'
    idFriend = db.Column(db.Integer(), primary_key=True)
    creacion = db.Column(db.db.DateTime(), default=db.db.DateTime.now())    
    estadoSolicitud = db.Column(db.Boolean(), nullable=False, unique=False)
    idRemitente =  relationship("User", secondary=friendship, 
                           primaryjoin=id==friendship.c.friend_a_id,)
    idReceptor = relationship("User", secondary=friendship, 
                           primaryjoin=id==friendship.c.friend_b_id,)