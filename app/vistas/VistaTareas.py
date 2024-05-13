from flask import request, Response
from flask_jwt_extended import jwt_required
from flask_restful import Resource
from marshmallow import ValidationError
from modelos.modelos import Tareas, TareasSchema, db, StatusEnum
from sqlalchemy import exc

import asyncio
import uuid
import json
from google.cloud import pubsub_v1
#from celery import Celery

#import asyncio

tareas_schema = TareasSchema()


#celery = Celery('tasks', backend='redis://10.128.0.13/0', broker='redis://10.128.0.13/0')

topic_name = 'projects/{project_id}/topics/{topic}'.format(
    project_id="idrl-videos-202410",
    topic='MyTopic',  # Set this to something appropriate.
)

def sendFile(filename):
    try:
        id = str(uuid.uuid4())
        tarea = tareas_schema.load({"id_task":id}, session=db.session)
        db.session.add(tarea)
        db.session.commit()
        publisher = pubsub_v1.PublisherClient()
        data = {
            'url': filename,
            'id': id
        }
        future = publisher.publish(topic_name, data=json.dumps(data).encode('utf-8'))
        result = future.result()
        return tareas_schema.dump(tarea), 201
    except ValidationError as validation_error:
        return validation_error.messages, 400
    except exc.IntegrityError as e:
        db.session.rollback()
        return {'mensaje': 'Hubo un error creando la tarea. Revise los datos proporcionados'}, 400

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
        filename = request.json['filename']
        return sendFile(filename)
