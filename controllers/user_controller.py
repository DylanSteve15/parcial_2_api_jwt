# controllers/user_controller.py
import logging
from flask import Blueprint, request, jsonify
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    jwt_required,
    get_jwt_identity,
    get_jwt
)
from functools import wraps
from services.user_service import UserService
from config.database import get_db_session
from flask_jwt_extended.exceptions import NoAuthorizationError

# Configuración de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Inicializar blueprint y servicio
user_bp = Blueprint("users", __name__)
service = UserService(next(get_db_session()))

# Lista para almacenar tokens invalidados (logout)
blacklist = set()

# ============================================================
# 🔐 MANEJO DE ERRORES JWT
# ============================================================
def register_jwt_error_handlers(app):
    @app.errorhandler(NoAuthorizationError)
    def handle_no_auth_error(e):
        logger.warning("Intento de acceso sin autenticación JWT.")
        return jsonify({
            'error': 'No autenticado. Debe enviar un token JWT válido en el header Authorization.'
        }), 401

    @app.errorhandler(403)
    def forbidden(e):
        return jsonify({'error': 'Acceso denegado: Permisos insuficientes'}), 403


# ============================================================
# 🔑 DECORADOR DE ROLES
# ============================================================
def role_required(required_role):
    def decorator(f):
        @jwt_required()
        @wraps(f)
        def decorated_function(*args, **kwargs):
            current_user_id = get_jwt_identity()
            user = service.obtener_usuario_por_id(current_user_id)
            if not user or user.role != required_role:
                logger.warning(f"Acceso denegado: usuario {current_user_id} sin rol {required_role}")
                return jsonify({'error': 'Rol requerido o permisos insuficientes'}), 403
            return f(*args, **kwargs)
        return decorated_function
    return decorator


# ============================================================
# 🧩 RUTAS DE AUTENTICACIÓN
# ============================================================
@user_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        return jsonify({"error": "El email y la contraseña son obligatorios."}), 400

    user = service.autenticar_usuario(email, password)
    if not user:
        logger.warning(f"Intento de login fallido para {email}")
        return jsonify({"error": "Credenciales inválidas"}), 401

    access_token = create_access_token(identity=user.id, additional_claims={"role": user.role})
    refresh_token = create_refresh_token(identity=user.id)

    logger.info(f"Usuario autenticado correctamente: {email}")
    return jsonify({
        "access_token": access_token,
        "refresh_token": refresh_token,
        "user": {
            "id": user.id,
            "email": user.email,
            "role": user.role
        }
    }), 200


@user_bp.route("/refresh", methods=["POST"])
@jwt_required(refresh=True)
def refresh():
    current_user = get_jwt_identity()
    new_access_token = create_access_token(identity=current_user)
    return jsonify({"access_token": new_access_token}), 200


@user_bp.route("/logout", methods=["POST"])
@jwt_required()
def logout():
    jti = get_jwt()["jti"]
    blacklist.add(jti)
    logger.info(f"Token agregado al blacklist (logout).")
    return jsonify({"message": "Logout exitoso."}), 200


# ============================================================
# 👤 CRUD DE USUARIOS
# ============================================================
@user_bp.route("/registry", methods=["POST"])  # 🔥 Ruta corregida para coincidir con tu frontend
def register():
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")
    role = data.get("role", "user")

    if not email or not password:
        return jsonify({"error": "El email y la contraseña son obligatorios."}), 400

    try:
        new_user = service.crear_usuario(email, password, role)
        return jsonify({
            "id": new_user.id,
            "email": new_user.email,
            "role": new_user.role
        }), 201
    except ValueError as e:
        return jsonify({"error": str(e)}), 400


@user_bp.route("/users", methods=["GET"])
@jwt_required()
def list_users():
    users = service.listar_usuarios()
    return jsonify([
        {"id": u.id, "email": u.email, "role": u.role}
        for u in users
    ]), 200


@user_bp.route("/users/<int:user_id>", methods=["GET"])
@jwt_required()
def get_user(user_id):
    user = service.obtener_usuario_por_id(user_id)
    if not user:
        return jsonify({"error": "Usuario no encontrado"}), 404
    return jsonify({
        "id": user.id,
        "email": user.email,
        "role": user.role
    }), 200


@user_bp.route("/users/<int:user_id>", methods=["PUT"])
@role_required("admin")
def update_user(user_id):
    data = request.get_json()
    updated = service.actualizar_usuario(
        user_id,
        email=data.get("email"),
        password=data.get("password"),
        role=data.get("role")
    )
    if updated:
        return jsonify({"message": "Usuario actualizado correctamente"}), 200
    return jsonify({"error": "Usuario no encontrado"}), 404


@user_bp.route("/users/<int:user_id>", methods=["DELETE"])
@role_required("admin")
def delete_user(user_id):
    deleted = service.eliminar_usuario(user_id)
    if deleted:
        return jsonify({"message": "Usuario eliminado correctamente"}), 200
    return jsonify({"error": "Usuario no encontrado"}), 404
