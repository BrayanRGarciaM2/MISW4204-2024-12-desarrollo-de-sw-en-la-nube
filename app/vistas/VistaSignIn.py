import re

from sqlalchemy import exc
from flask import request
from flask_jwt_extended import create_access_token, current_user, jwt_required
from flask_restful import Resource

from app.modelos.modelos import UsuarioSchema, Usuario, db

usuario_schema = UsuarioSchema()


class VistaSignIn(Resource):

    def validar_email(self, email):
        # Patrón para validar el email
        patron = r'^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w+$'

        if re.match(patron, email):
            return True
        else:
            return False

    def post(self):
        if request.json["password1"] != request.json["password2"]:
            return {"mensaje": "Las Passwords no coinciden"}, 400
        if not self.validar_email(request.json["email"]):
            return {"mensaje": "Body de Email incorrecto"}, 400
        try:
            nuevo_usuario = Usuario(usuario=request.json["username"], contrasena=request.json["password1"], email=request.json["email"])
            db.session.add(nuevo_usuario)
            db.session.commit()
        except exc.IntegrityError:
            db.session.rollback()
            return {"mensaje": "Ya existe un usuario con este identificador"}, 400
        token_de_acceso = create_access_token(identity=nuevo_usuario.id)
        return {"mensaje": "usuario creado", "token": token_de_acceso, "id": nuevo_usuario.id}, 201

    @jwt_required()
    def put(self, id_usuario):
        usuario_token = current_user
        if id_usuario != current_user.id:
            return {"mensaje": "Peticion invalida"}, 400
        usuario_token.contrasena = request.json.get("contrasena", usuario_token.contrasena)
        db.session.commit()
        return usuario_schema.dump(usuario_token)
