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

# Inicializar blueprint
user_bp = Blueprint("users", __name__)

# Lista para almacenar tokens invalidados (logout)
blacklist = set()

# ============================================================
# 🔐 MANEJO DE ERRORES JWT
# ============================================================
def register_jwt_error_handlers(app):
    from flask_jwt_extended.exceptions import JWTDecodeError, InvalidHeaderError, WrongTokenError
    
    @app.errorhandler(NoAuthorizationError)
    def handle_no_auth_error(e):
        logger.warning("Intento de acceso sin autenticación JWT.")
        return jsonify({
            'error': 'No autenticado. Debe enviar un token JWT válido en el header Authorization.'
        }), 401

    @app.errorhandler(422)
    def handle_unprocessable_entity(e):
        error_msg = str(e) if e else 'Error desconocido'
        logger.warning(f"Error 422: {error_msg}")
        # Flask-JWT-Extended devuelve 422 para errores de token
        # Log más detallado para debugging
        import traceback
        logger.debug(f"Traceback del error 422: {traceback.format_exc()}")
        return jsonify({
            'error': f'Token JWT inválido o mal formado: {error_msg}. Por favor, inicia sesión nuevamente.'
        }), 422

    @app.errorhandler(JWTDecodeError)
    def handle_jwt_decode_error(e):
        logger.warning(f"Error decodificando JWT: {str(e)}")
        return jsonify({
            'error': 'Token JWT inválido. Por favor, inicia sesión nuevamente.'
        }), 422

    @app.errorhandler(InvalidHeaderError)
    def handle_invalid_header_error(e):
        logger.warning(f"Error en header JWT: {str(e)}")
        return jsonify({
            'error': 'Header de autorización inválido. Formato esperado: Bearer <token>'
        }), 422

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
            # Convertir a int si viene como string
            user_id_int = int(current_user_id) if isinstance(current_user_id, str) else current_user_id
            db = next(get_db_session())
            service = UserService(db)
            try:
                user = service.obtener_usuario_por_id(user_id_int)
                if not user or user.role != required_role:
                    logger.warning(f"Acceso denegado: usuario {current_user_id} sin rol {required_role}")
                    return jsonify({'error': 'Rol requerido o permisos insuficientes'}), 403
                return f(*args, **kwargs)
            finally:
                db.close()
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

    db = next(get_db_session())
    service = UserService(db)
    try:
        user = service.autenticar_usuario(email, password)
        if not user:
            logger.warning(f"Intento de login fallido para {email}")
            return jsonify({"error": "Credenciales inválidas"}), 401

        # Flask-JWT-Extended requiere que identity sea una cadena
        access_token = create_access_token(identity=str(user.id), additional_claims={"role": user.role})
        refresh_token = create_refresh_token(identity=str(user.id))

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
    finally:
        db.close()


@user_bp.route("/refresh", methods=["POST"])
@jwt_required(refresh=True)
def refresh():
    current_user = get_jwt_identity()
    # Asegurar que identity sea string
    new_access_token = create_access_token(identity=str(current_user))
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

    # Verificar si hay un token de admin (opcional)
    is_admin = False
    try:
        from flask_jwt_extended import verify_jwt_in_request, get_jwt
        verify_jwt_in_request(optional=True)
        claims = get_jwt()
        if claims and claims.get("role") == "admin":
            is_admin = True
            # Si es admin, solo puede crear usuarios normales
            role = "user"
    except:
        pass

    db = next(get_db_session())
    service = UserService(db)
    try:
        # Si no es admin y intenta crear admin, rechazar
        if not is_admin and role == "admin":
            existing_admin = service.obtener_usuario_por_id(1)  # Verificar si existe admin
            admin_users = [u for u in service.listar_usuarios() if u.role == "admin"]
            if admin_users:
                return jsonify({"error": "No se puede crear un administrador. Solo puede haber uno."}), 403
        
        new_user = service.crear_usuario(email, password, role)
        return jsonify({
            "id": new_user.id,
            "email": new_user.email,
            "role": new_user.role
        }), 201
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    finally:
        db.close()


@user_bp.route("/users", methods=["GET"])
@jwt_required()
def list_users():
    # Log del header de autorización para debugging
    auth_header = request.headers.get('Authorization', 'No header')
    logger.info(f"Authorization header recibido en /users: {auth_header[:50] if len(auth_header) > 50 else auth_header}...")
    db = next(get_db_session())
    service = UserService(db)
    try:
        users = service.listar_usuarios()
        return jsonify([
            {"id": u.id, "email": u.email, "role": u.role}
            for u in users
        ]), 200
    finally:
        db.close()


@user_bp.route("/users/<int:user_id>", methods=["GET"])
@jwt_required()
def get_user(user_id):
    db = next(get_db_session())
    service = UserService(db)
    try:
        user = service.obtener_usuario_por_id(user_id)
        if not user:
            return jsonify({"error": "Usuario no encontrado"}), 404
        return jsonify({
            "id": user.id,
            "email": user.email,
            "role": user.role
        }), 200
    finally:
        db.close()


@user_bp.route("/users/<int:user_id>", methods=["PUT"])
@jwt_required()
def update_user(user_id):
    """
    Actualiza un usuario.
    - Un usuario puede editar su propio perfil (email y password)
    - Solo un admin puede cambiar el rol de un usuario
    - Un admin puede editar cualquier usuario
    """
    data = request.get_json()
    current_user_id = get_jwt_identity()
    current_user_id = int(current_user_id) if isinstance(current_user_id, str) else current_user_id
    
    db = next(get_db_session())
    service = UserService(db)
    try:
        # Obtener el usuario actual para verificar su rol
        current_user = service.obtener_usuario_por_id(current_user_id)
        is_admin = current_user and current_user.role == "admin"
        
        # Verificar permisos: solo admin o el mismo usuario puede editar
        if current_user_id != user_id and not is_admin:
            logger.warning(f"Acceso denegado: usuario {current_user_id} intenta editar a {user_id}")
            return jsonify({"error": "Solo puedes editar tu propio perfil o ser administrador"}), 403
        
        # Si no es admin, no puede cambiar el rol
        if not is_admin and data.get("role"):
            logger.warning(f"Intento no autorizado de cambiar rol por usuario {current_user_id}")
            return jsonify({"error": "No tienes permisos para cambiar roles"}), 403
        
        updated = service.actualizar_usuario(
            user_id,
            email=data.get("email"),
            password=data.get("password"),
            role=data.get("role") if is_admin else None
        )
        if updated:
            logger.info(f"Usuario {user_id} actualizado por {current_user_id}")
            return jsonify({
                "message": "Usuario actualizado correctamente",
                "user": {
                    "id": updated.id,
                    "email": updated.email,
                    "role": updated.role
                }
            }), 200
        return jsonify({"error": "Usuario no encontrado"}), 404
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    finally:
        db.close()


@user_bp.route("/users/<int:user_id>", methods=["DELETE"])
@role_required("admin")
def delete_user(user_id):
    db = next(get_db_session())
    service = UserService(db)
    try:
        deleted = service.eliminar_usuario(user_id)
        if deleted:
            return jsonify({"message": "Usuario eliminado correctamente"}), 200
        return jsonify({"error": "Usuario no encontrado"}), 404
    finally:
        db.close()
