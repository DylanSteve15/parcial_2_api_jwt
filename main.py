from models.db import Base
from config.database import engine
from flask import Flask, send_from_directory
from config.jwt import *
from controllers.user_controller import user_bp, register_jwt_error_handlers
from controllers.horario_controller import horario_bp
from flask_jwt_extended import JWTManager
from dotenv import load_dotenv
import os
import secrets
import logging

# Configurar logs
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Verifica y crea .env si no existe
if not os.path.exists('.env'):
    logger.info("Creando archivo .env con configuración predeterminada...")
    with open('.env', 'w') as f:
        f.write(f"JWT_SECRET_KEY={secrets.token_hex(32)}\n")
        f.write("MYSQL_URI=sqlite:///horarios_local.db\n")  # Base local por defecto
    logger.info("Archivo .env creado. Reinicia la app para cargar cambios.")
    load_dotenv()

# Cargar variables de entorno
load_dotenv()

app = Flask(__name__, static_folder='static')

# Configuración del JWT
app.config['JWT_SECRET_KEY'] = JWT_SECRET_KEY
app.config['JWT_TOKEN_LOCATION'] = JWT_TOKEN_LOCATION
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = JWT_ACCESS_TOKEN_EXPIRES
app.config['JWT_HEADER_NAME'] = JWT_HEADER_NAME
app.config['JWT_HEADER_TYPE'] = JWT_HEADER_TYPE

jwt = JWTManager(app)

# Registrar Blueprints
app.register_blueprint(user_bp, url_prefix='/api')
app.register_blueprint(horario_bp, url_prefix='/api')

# Registrar manejo de errores JWT
register_jwt_error_handlers(app)

# Ruta principal
@app.route('/')
def index():
    return send_from_directory('static', 'index.html')

# Inicializar la base de datos
if __name__ == "__main__":
    Base.metadata.create_all(engine)
    logger.info("Tablas creadas correctamente.")
    app.run(debug=True)
