from sqlalchemy import exc
from flask import request, Response
from flask_jwt_extended import create_access_token, current_user, jwt_required
from flask_restful import Resource
from marshmallow import ValidationError

import os

from modelos.modelos import Tareas, TareasSchema, db, StatusEnum

from celery import Celery

from datetime import datetime

tareas_schema = TareasSchema()


celery = Celery('task', backend='redis://redis:6379/0', broker='redis://redis:6379/0')

@celery.task
def editVideo(url):
    os.system('youtube-dl '+url)
    """ respuesta = requests.get(url)
    
    if respuesta.status_code == 200:
        with open('/usr/src/app/video_descargado.mp4', 'wb') as archivo:
            archivo.write(respuesta.content)
    else:
        print("No se pudo descargar el video. Código de estado:", respuesta.status_code)
 """
    


class VistaTareas(Resource):

    @jwt_required()
    def get(self):
        limit = request.args.get('max')
        order = request.args.get('order')
        tareas = db.session.query(Tareas)

        if limit is not None:
            tareas = tareas.limit(limit)
        if order is not None:
            tareas = tareas.order_by(Tareas.id.asc)

        tareas = tareas.all()

        if not tareas:
            return Response(status=204)
        else:
            return tareas_schema.dump(tareas, many=True), 200
        
    @jwt_required()
    def post(self):
        try:
            fileName = request.json['fileName']
            result = editVideo(fileName)
            tarea = tareas_schema.load({"id":result.id}, session=db.session)
            db.session.add(tarea)
            db.session.commit()
        except ValidationError as validation_error:
            return validation_error.messages, 400
        except exc.IntegrityError as e:
            db.session.rollback()
            return {'mensaje': 'Hubo un error creando la tarea. Revise los datos proporcionados'}, 400
        return tareas_schema.dump(tarea), 201