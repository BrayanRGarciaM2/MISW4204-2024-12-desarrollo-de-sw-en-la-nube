from flask import request, Response
from flask_jwt_extended import jwt_required
from flask_restful import Resource
from marshmallow import ValidationError
from modelos.modelos import Tareas, TareasSchema, db, StatusEnum
from sqlalchemy import exc

import asyncio

from celery import Celery

tareas_schema = TareasSchema()


celery = Celery('tasks', backend='redis://redis:6379/0', broker='redis://redis:6379/0')

async def esperar(result):
    while not result.ready():
        await asyncio.sleep(1)

    if result.state == "SUCCESS":
        tareas = Tareas.query.filter(Tareas.id_task == result.id).one_or_none()
        tareas_schema.load({'status': "PROCESSED", 'result': result.result}, session=db.session, instance=tareas, partial=True)
        db.session.commit()
    else:
        print("La tarea falló o está en un estado desconocido.")

async def sendFile(filename):
    try:
        result = celery.send_task('tasks.edit', args=[filename])
        tarea = tareas_schema.load({"id_task":result.id}, session=db.session)
        db.session.add(tarea)
        db.session.commit()
        await asyncio.create_task(esperar(result))
    except ValidationError as validation_error:
        return validation_error.messages, 400
    except exc.IntegrityError as e:
        db.session.rollback()
        return {'mensaje': 'Hubo un error creando la tarea. Revise los datos proporcionados'}, 400
    return tareas_schema.dump(tarea), 201

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
        return asyncio.run(sendFile(filename))