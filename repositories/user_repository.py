import logging
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from models.user_model import User

# Configuración del logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class UserRepository:
    """
    Repositorio responsable de gestionar las operaciones CRUD sobre el modelo User.
    """

    def __init__(self, db_session: Session):
        """
        Inicializa el repositorio con una sesión de base de datos.
        """
        self.db = db_session

    # ---------------------------------------------------------------------
    # Métodos CRUD
    # ---------------------------------------------------------------------

    def get_all_users(self) -> List[User]:
        """
        Recupera todos los usuarios de la base de datos.
        :return: Lista de instancias User.
        """
        logger.info("Obteniendo todos los usuarios desde la base de datos...")
        try:
            users = self.db.query(User).all()
            logger.info(f"{len(users)} usuarios encontrados.")
            return users
        except SQLAlchemyError as e:
            logger.error(f"Error al obtener usuarios: {e}")
            return []

    def get_user_by_id(self, user_id: int) -> Optional[User]:
        """
        Busca un usuario por su ID.
        :param user_id: ID del usuario a buscar.
        :return: Instancia de User si existe, o None.
        """
        logger.info(f"Buscando usuario con ID: {user_id}")
        try:
            return self.db.query(User).filter(User.id == user_id).first()
        except SQLAlchemyError as e:
            logger.error(f"Error al buscar usuario por ID: {e}")
            return None

    def get_user_by_username(self, username: str) -> Optional[User]:
        """
        Busca un usuario por su nombre de usuario.
        :param username: Nombre de usuario.
        :return: Instancia de User si existe, o None.
        """
        logger.info(f"Buscando usuario con nombre: {username}")
        try:
            return self.db.query(User).filter(User.username == username).first()
        except SQLAlchemyError as e:
            logger.error(f"Error al buscar usuario por nombre: {e}")
            return None

    def create_user(self, username: str, password: str) -> Optional[User]:
        """
        Crea un nuevo usuario y lo almacena en la base de datos.
        :param username: Nombre del usuario.
        :param password: Contraseña (hash).
        :return: El usuario creado o None si ocurre un error.
        """
        logger.info(f"Creando nuevo usuario: {username}")
        try:
            new_user = User(username=username, password=password)
            self.db.add(new_user)
            self.db.commit()
            self.db.refresh(new_user)
            logger.info(f"Usuario '{username}' creado con ID {new_user.id}")
            return new_user
        except SQLAlchemyError as e:
            logger.error(f"Error al crear usuario: {e}")
            self.db.rollback()
            return None

    def update_user(
        self, user_id: int, username: Optional[str] = None, password: Optional[str] = None
    ) -> Optional[User]:
        """
        Actualiza la información de un usuario.
        :param user_id: ID del usuario a actualizar.
        :param username: Nuevo nombre (opcional).
        :param password: Nueva contraseña (opcional).
        :return: Usuario actualizado o None.
        """
        user = self.get_user_by_id(user_id)
        if not user:
            logger.warning(f"No se encontró usuario con ID {user_id} para actualizar.")
            return None

        try:
            if username:
                user.username = username
            if password:
                user.password = password
            self.db.commit()
            self.db.refresh(user)
            logger.info(f"Usuario {user_id} actualizado correctamente.")
            return user
        except SQLAlchemyError as e:
            logger.error(f"Error al actualizar usuario: {e}")
            self.db.rollback()
            return None

    def delete_user(self, user_id: int) -> bool:
        """
        Elimina un usuario por su ID.
        :param user_id: ID del usuario a eliminar.
        :return: True si se eliminó, False si no existe o ocurrió un error.
        """
        user = self.get_user_by_id(user_id)
        if not user:
            logger.warning(f"No se encontró usuario con ID {user_id} para eliminar.")
            return False

        try:
            self.db.delete(user)
            self.db.commit()
            logger.info(f"Usuario {user_id} eliminado correctamente.")
            return True
        except SQLAlchemyError as e:
            logger.error(f"Error al eliminar usuario: {e}")
            self.db.rollback()
            return False
