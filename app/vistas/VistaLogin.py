from flask import request
from flask_jwt_extended import create_access_token
from flask_restful import Resource

from modelos.modelos import Usuario, UsuarioSchema, db

usuario_schema = UsuarioSchema()

class VistaLogin(Resource):

    def post(self):
        usuario_db = db.session.query(Usuario).filter(Usuario.usuario == request.json["username"],
                    Usuario.contrasena == request.json["password"]).first()
        if usuario_db is None:
            return "Verifique los datos ingresados", 404
        usuario = usuario_db
        token_de_acceso = create_access_token(identity=usuario.id)

        return {"mensaje": "Inicio de sesion exitoso", "token": token_de_acceso}
