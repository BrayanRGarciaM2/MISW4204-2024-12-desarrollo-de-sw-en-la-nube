from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_restful import Api

from modelos.modelos import db, Usuario
from vistas.VistaSignIn import VistaSignIn
from vistas.VistaLogin import VistaLogin
from vistas.VistaTareas import VistaTareas
from vistas.VistaTarea import VistaTarea


def create_flask_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:postgres@db:5432/videos'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['JWT_SECRET_KEY'] = 'frase-secreta'
    app.config['PROPAGATE_EXCEPTIONS'] = True

    app_context = app.app_context()
    app_context.push()
    add_urls(app)
    CORS(app)

    jwt = JWTManager(app)

    @jwt.user_lookup_loader
    def user_lookup_callback(_jwt_header, jwt_data):
        identity = jwt_data["sub"]
        return Usuario.query.filter_by(id=identity).one_or_none()

    return app


def add_urls(app):
    api = Api(app)
    api.add_resource(VistaSignIn, '/api/auth/signup')
    api.add_resource(VistaLogin, '/api/auth/login')
    api.add_resource(VistaTareas, '/api/tasks')
    api.add_resource(VistaTarea, '/api/tasks/<int:id_task>')

app = create_flask_app()
db.init_app(app)
db.create_all()


