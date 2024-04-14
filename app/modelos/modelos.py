from flask_sqlalchemy import SQLAlchemy
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from marshmallow import fields
from datetime import datetime
import enum

db = SQLAlchemy()

class StatusEnum(enum.Enum):
    UPLOADED = "uploaded"
    PROCESSED = "processed"

class Usuario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    usuario = db.Column(db.String(50), nullable=False, unique=True)
    contrasena = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(60), nullable=False, unique=True)

class Tareas(db.Model):
    id = db.Column(db.Integer, unique=True, primary_key=True)
    status = db.Column(db.Enum(StatusEnum), default=StatusEnum.UPLOADED, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.now)
    result = db.Column(db.Text, default="NULL", nullable=True)

class UsuarioSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Usuario
        include_relationships = True
        load_instance = True
        exclude = ('contrasena',)

class TareasSchema(SQLAlchemyAutoSchema):
    status = fields.Enum(StatusEnum)
    class Meta:
        model = Tareas
        include_relationships = True
        load_instance = True