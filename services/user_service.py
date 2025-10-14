#
import logging
from typing import List, Optional
from models.user_model import User
from repositories.user_repository import UserRepository
from werkzeug.security import generate_password_hash, check_password_hash

# Configuración del logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class UserService:
    """
    Servicio que gestiona la lógica de negocio relacionada con los usuarios.
    Se encarga de orquestar la comunicación entre controladores y repositorios,
    aplicando validaciones, reglas y transformaciones de datos.
    """

    def __init__(self, user_repository: UserRepository):
        """
        Inicializa el servicio con una instancia del repositorio de usuarios.
        """
        self.user_repository = user_repository

    # ---------------------------------------------------------------------
    # Métodos de negocio
    # ---------------------------------------------------------------------

    def listar_usuarios(self) -> List[User]:
        """
        Devuelve la lista de todos los usuarios registrados.
        """
        logger.info("Listando todos los usuarios registrados...")
        return self.user_repository.get_all_users()

    def obtener_usuario_por_id(self, user_id: int) -> Optional[User]:
        """
        Devuelve un usuario específico por su ID.
        """
        logger.info(f"Obteniendo usuario con ID {user_id}...")
        return self.user_repository.get_user_by_id(user_id)

    def crear_usuario(self, username: str, password: str) -> Optional[User]:
        """
        Registra un nuevo usuario después de validar que no exista el mismo username.
        La contraseña se almacena de forma encriptada.
        """
        logger.info(f"Intentando crear usuario '{username}'...")

        # Validar si el usuario ya existe
        existing_user = self.user_repository.get_user_by_username(username)
        if existing_user:
            logger.warning(f"El nombre de usuario '{username}' ya existe.")
            return None

        # Encriptar la contraseña antes de guardarla
        hashed_password = generate_password_hash(password)
        logger.info(f"Contraseña encriptada para el usuario '{username}'")

        return self.user_repository.create_user(username=username, password=hashed_password)

    def autenticar_usuario(self, username: str, password: str) -> Optional[User]:
        """
        Verifica las credenciales del usuario.
        Si son correctas, devuelve la instancia del usuario.
        """
        logger.info(f"Autenticando usuario '{username}'...")
        user = self.user_repository.get_user_by_username(username)

        if not user:
            logger.warning(f"Usuario '{username}' no encontrado.")
            return None

        if check_password_hash(user.password, password):
            logger.info(f"Usuario '{username}' autenticado correctamente.")
            return user

        logger.warning("Contraseña incorrecta.")
        return None

    def actualizar_usuario(
        self, user_id: int, username: Optional[str] = None, password: Optional[str] = None
    ) -> Optional[User]:
        """
        Actualiza los datos de un usuario, encriptando la nueva contraseña si se modifica.
        """
        logger.info(f"Actualizando usuario con ID {user_id}...")

        hashed_password = None
        if password:
            hashed_password = generate_password_hash(password)
            logger.info(f"Nueva contraseña encriptada para el usuario ID {user_id}")

        return self.user_repository.update_user(user_id, username=username, password=hashed_password)

    def eliminar_usuario(self, user_id: int) -> bool:
        """
        Elimina un usuario por su ID.
        """
        logger.info(f"Intentando eliminar usuario con ID {user_id}...")
        return self.user_repository.delete_user(user_id)
