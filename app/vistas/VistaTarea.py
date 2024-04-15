from flask import request, Response
from flask_jwt_extended import jwt_required
from flask_restful import Resource
from marshmallow import ValidationError
from modelos.modelos import Tareas, TareasSchema, db, StatusEnum
from sqlalchemy import exc

tareas_schema = TareasSchema()

class VistaTarea(Resource):

    @jwt_required()
    def get(self, id_task):
        tarea = Tareas.query.filter(Tareas.id == id_task).one_or_none()
        if tarea:
            return tareas_schema.dump(tarea)
        
        return "Tarea no encontrada"
        
    @jwt_required()
    def delete(self, id_task):
        tarea = Tareas.query.filter(Tareas.id == id_task).one_or_none()
        if tarea:
            db.session.delete(tarea)
            db.session.commit()
            return "Tarea eliminada con éxito"
        
        return "Tarea no encontrada"