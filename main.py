# main.py
# Punto de entrada principal de la API Flask para gestión de usuarios y horarios

from flask import Flask, jsonify
from flask_cors import CORS
from config.database import init_db
from controllers.user_controller import user_bp
from controllers.horario_controller import horario_bp
import os

def create_app():
    """
    Crea e inicializa la aplicación Flask.
    Configura la base de datos, CORS y los controladores (blueprints).
    """
    app = Flask(__name__)

    # ==============================
    # CONFIGURACIÓN GENERAL
    # ==============================
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'clave_super_secreta')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///horarios_local.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # ==============================
    # CONFIGURAR CORS
    # ==============================
    CORS(app, resources={r"/api/*": {"origins": "*"}})

    # ==============================
    # INICIALIZAR BASE DE DATOS
    # ==============================
    init_db(app)

    # ==============================
    # REGISTRAR BLUEPRINTS (RUTAS)
    # ==============================
    app.register_blueprint(user_bp, url_prefix="/api/users")
    app.register_blueprint(horario_bp, url_prefix="/api/horarios")

    # ==============================
    # RUTA DE PRUEBA / STATUS
    # ==============================
    @app.route("/api", methods=["GET"])
    def index():
        """
        Ruta base para verificar el estado de la API.
        """
        return jsonify({
            "status": "ok",
            "message": "API Flask Horarios funcionando correctamente 🚀"
        }), 200

    # ==============================
    # MANEJADORES DE ERRORES GLOBALES
    # ==============================
    @app.errorhandler(404)
    def not_found_error(e):
        return jsonify({"error": "Ruta no encontrada"}), 404

    @app.errorhandler(500)
    def internal_error(e):
        return jsonify({"error": "Error interno del servidor"}), 500

    return app


if __name__ == "__main__":
    # Crear e iniciar la aplicación
    app = create_app()

    # Puerto y modo debug configurables por entorno
    port = int(os.getenv("PORT", 5000))
    debug_mode = os.getenv("FLASK_ENV", "development") == "development"

    print(f"\n🚀 Servidor Flask iniciado en http://127.0.0.1:{port}/api\n")

    app.run(host="0.0.0.0", port=port, debug=debug_mode)
