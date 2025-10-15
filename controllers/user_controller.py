import logging
from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import (
    create_access_token, 
    create_refresh_token, 
    jwt_required, 
    get_jwt_identity, 
    get_jwt
)
from flask_jwt_extended.exceptions import NoAuthorizationError
from functools import wraps

from services.user_service import UserService  # Nombre ajustado a tu estructura
from config.database import get_db_session

# Configuración de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Inicializar blueprint y servicio
user_bp = Blueprint('users', __name__)
service = UserService(next(get_db_session()))

# Blacklist para manejar el logout de tokens
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
            user = service.get_user_by_id(int(current_user_id))
            if not user or str(user.id_perfil) != str(required_role):
                logger.warning(f"Acceso denegado: usuario {current_user_id} sin rol {required_role}")
                return jsonify({'error': 'Rol requerido o permisos insuficientes'}), 403
            return f(*args, **kwargs)
        return decorated_function
    return decorator

# ============================================================
# 🧩 RUTAS DE AUTENTICACIÓN
# ============================================================
@user_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    usuario = data.get('usuario')
    clave = data.get('clave')

    if not usuario or not clave:
        logger.warning("Login fallido: usuario o clave no proporcionados.")
        return jsonify({'error': 'El usuario y la clave son obligatorios.'}), 400

    user = service.authenticate_user(usuario, clave)
    if user:
        access_token = create_access_token(identity=str(user.identificacion), additional_claims={'rol': user.id_perfil})
        refresh_token = create_refresh_token(identity=str(user.identificacion))
        logger.info(f"Usuario autenticado: {usuario}")
        return jsonify({'access_token': access_token, 'refresh_token': refresh_token}), 200

    logger.warning(f"Login fallido para usuario: {usuario}")
    return jsonify({'error': 'Credenciales inválidas.'}), 401


@user_bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    current_user = get_jwt_identity()
    access_token = create_access_token(identity=current_user)
    return jsonify({'access_token': access_token}), 200


@user_bp.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    jti = get_jwt()['jti']
    blacklist.add(jti)
    return jsonify({'message': 'Logout exitoso.'}), 200

# ============================================================
# 👤 CRUD DE USUARIOS
# ============================================================
@user_bp.route('/registry', methods=['POST'])
def create_user():
    data = request.get_json()
    identificacion = data.get('identificacion')
    nombre = data.get('nombre')
    apellido = data.get('apellido')
    email = data.get('email')
    telefono = data.get('telefono')
    usuario = data.get('usuario')
    clave = data.get('clave')
    id_perfil = data.get('id_perfil', 2)  # 1=admin, 2=usuario normal

    if not usuario or not clave:
        logger.warning("Registro fallido: usuario o clave no proporcionados.")
        return jsonify({'error': 'El usuario y la clave son obligatorios.'}), 400

    try:
        nuevo_usuario = service.create_user(
            identificacion, nombre, apellido, email, telefono, usuario, clave, id_perfil
        )
        logger.info(f"Usuario creado: {usuario}")
        return jsonify({
            'identificacion': nuevo_usuario.identificacion,
            'usuario': nuevo_usuario.usuario,
            'rol': nuevo_usuario.id_perfil
        }), 201
    except ValueError as e:
        logger.warning(f"Error al crear usuario: {str(e)}")
        return jsonify({'error': str(e)}), 400

@user_bp.route('/users', methods=['GET'])
@role_required(1)  # Solo admin (id_perfil = 1)
def get_users():
    users = service.get_all_users()
    logger.info("Consulta de todos los usuarios.")
    return jsonify([
        {
            'identificacion': u.identificacion,
            'nombre': u.nombre,
            'apellido': u.apellido,
            'email': u.email,
            'telefono': u.telefono,
            'usuario': u.usuario,
            'rol': u.id_perfil
        } for u in users
    ]), 200

@user_bp.route('/users/<int:identificacion>', methods=['GET'])
@jwt_required()
def get_user(identificacion):
    user = service.get_user_by_id(identificacion)
    if user:
        logger.info(f"Consulta de usuario por ID: {identificacion}")
        return jsonify({
            'identificacion': user.identificacion,
            'nombre': user.nombre,
            'apellido': user.apellido,
            'email': user.email,
            'telefono': user.telefono,
            'usuario': user.usuario,
            'rol': user.id_perfil
        }), 200
    logger.warning(f"Usuario no encontrado: {identificacion}")
    return jsonify({'error': 'Usuario no encontrado'}), 404

@user_bp.route('/users/<int:identificacion>', methods=['PUT'])
@role_required(1)
def update_user(identificacion):
    data = request.get_json()
    actualizado = service.update_user(identificacion, data)
    if actualizado:
        logger.info(f"Usuario actualizado: {identificacion}")
        return jsonify({'message': 'Usuario actualizado correctamente'}), 200
    logger.warning(f"Usuario no encontrado para actualizar: {identificacion}")
    return jsonify({'error': 'Usuario no encontrado'}), 404

@user_bp.route('/users/<int:identificacion>', methods=['DELETE'])
@role_required(1)
def delete_user(identificacion):
    eliminado = service.delete_user(identificacion)
    if eliminado:
        logger.info(f"Usuario eliminado: {identificacion}")
        return jsonify({'message': 'Usuario eliminado correctamente'}), 200
    logger.warning(f"Usuario no encontrado para eliminar: {identificacion}")
    return jsonify({'error': 'Usuario no encontrado'}), 404
