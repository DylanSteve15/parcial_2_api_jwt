import logging
from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import create_access_token, jwt_required
from flask_jwt_extended.exceptions import NoAuthorizationError

from config.database import get_db_session
from services.user_service import UserService  # Ajustado al nombre correcto

# Configurar logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Crear Blueprint
user_bp = Blueprint('user_bp', __name__)

# Instancia global del servicio
service = UserService(get_db_session())


# ------------------ Manejo de errores JWT ------------------
def register_jwt_error_handlers(app):
    @app.errorhandler(NoAuthorizationError)
    def handle_no_auth_error(e):
        logger.warning("Intento de acceso sin autenticación JWT")
        return (
            jsonify({
                'error': 'No autenticado. Debe enviar un token JWT válido en el header Authorization.'
            }),
            401,
            {'Content-Type': 'application/json; charset=utf-8'}
        )


# ------------------ LOGIN ------------------
@user_bp.route('/login', methods=['POST'])
def login():
    """
    POST /login
    Autentica un usuario y genera un token JWT si las credenciales son válidas.
    """
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        logger.warning("Intento de login sin usuario o contraseña")
        return (
            jsonify({'error': 'El nombre de usuario y la contraseña son obligatorios'}),
            400,
            {'Content-Type': 'application/json; charset=utf-8'}
        )

    user = service.authenticate_user(username, password)
    if user:
        access_token = create_access_token(identity=str(user.id))
        logger.info(f"Usuario autenticado correctamente: {username}")
        return (
            jsonify({
                'message': 'Autenticación exitosa',
                'access_token': access_token,
                'user': {'id': user.id, 'username': user.username}
            }),
            200,
            {'Content-Type': 'application/json; charset=utf-8'}
        )

    logger.warning(f"Credenciales inválidas para usuario: {username}")
    return (
        jsonify({'error': 'Credenciales inválidas'}),
        401,
        {'Content-Type': 'application/json; charset=utf-8'}
    )


# ------------------ REGISTRO ------------------
@user_bp.route('/register', methods=['POST'])
def register_user():
    """
    POST /register
    Crea un nuevo usuario en el sistema.
    Cuerpo JSON esperado:
    {
        "username": "dylan",
        "password": "1234"
    }
    """
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        logger.warning("Intento de registro con campos vacíos")
        return (
            jsonify({'error': 'El nombre de usuario y la contraseña son obligatorios'}),
            400,
            {'Content-Type': 'application/json; charset=utf-8'}
        )

    user = service.create_user(username, password)
    logger.info(f"Nuevo usuario registrado: {username}")
    return (
        jsonify({
            'message': 'Usuario creado exitosamente',
            'user': {'id': user.id, 'username': user.username}
        }),
        201,
        {'Content-Type': 'application/json; charset=utf-8'}
    )


# ------------------ CONSULTAR USUARIOS ------------------
@user_bp.route('/users', methods=['GET'])
@jwt_required()
def listar_usuarios():
    """
    GET /users
    Retorna todos los usuarios registrados.
    """
    logger.info("Consulta de todos los usuarios")
    users = service.get_all_users()
    return (
        jsonify([
            {'id': u.id, 'username': u.username}
            for u in users
        ]),
        200,
        {'Content-Type': 'application/json; charset=utf-8'}
    )


@user_bp.route('/users/<int:user_id>', methods=['GET'])
@jwt_required()
def obtener_usuario(user_id):
    """
    GET /users/<user_id>
    Recupera un usuario por su ID.
    """
    logger.info(f"Consultando usuario con ID: {user_id}")
    user = service.get_user_by_id(user_id)
    if user:
        return (
            jsonify({'id': user.id, 'username': user.username}),
            200,
            {'Content-Type': 'application/json; charset=utf-8'}
        )

    logger.warning(f"Usuario no encontrado: {user_id}")
    return (
        jsonify({'error': 'Usuario no encontrado'}),
        404,
        {'Content-Type': 'application/json; charset=utf-8'}
    )


# ------------------ ACTUALIZAR USUARIO ------------------
@user_bp.route('/users/<int:user_id>', methods=['PUT'])
@jwt_required()
def actualizar_usuario(user_id):
    """
    PUT /users/<user_id>
    Actualiza los datos de un usuario (username y/o password).
    """
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    logger.info(f"Actualizando usuario con ID: {user_id}")
    user = service.update_user(user_id, username, password)
    if user:
        return (
            jsonify({'id': user.id, 'username': user.username}),
            200,
            {'Content-Type': 'application/json; charset=utf-8'}
        )

    logger.warning(f"No se encontró usuario con ID: {user_id} para actualizar")
    return (
        jsonify({'error': 'Usuario no encontrado'}),
        404,
        {'Content-Type': 'application/json; charset=utf-8'}
    )


# ------------------ ELIMINAR USUARIO ------------------
@user_bp.route('/users/<int:user_id>', methods=['DELETE'])
@jwt_required()
def eliminar_usuario(user_id):
    """
    DELETE /users/<user_id>
    Elimina un usuario del sistema por su ID.
    """
    logger.info(f"Intentando eliminar usuario con ID: {user_id}")
    eliminado = service.delete_user(user_id)
    if eliminado:
        return (
            jsonify({'message': 'Usuario eliminado correctamente'}),
            200,
            {'Content-Type': 'application/json; charset=utf-8'}
        )

    logger.warning(f"Usuario no encontrado para eliminar: {user_id}")
    return (
        jsonify({'error': 'Usuario no encontrado'}),
        404,
        {'Content-Type': 'application/json; charset=utf-8'}
    )
