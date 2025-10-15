#repositories/user_repository
import logging
from sqlalchemy.orm import Session
from models.user_model import User
import bcrypt

# Configuración de logs
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class UserRepository:
    """
    Repositorio para gestionar las operaciones CRUD del modelo User.
    """
    def __init__(self, db_session: Session):
        self.db = db_session

    def get_all_users(self):
        logger.info("Obteniendo todos los usuarios desde el repositorio.")
        return self.db.query(User).all()

    def get_user_by_id(self, user_id: int):
        logger.info(f"Buscando usuario por ID: {user_id}")
        return self.db.query(User).filter(User.id == user_id).first()

    def get_user_by_email(self, email: str):
        logger.info(f"Buscando usuario por email: {email}")
        return self.db.query(User).filter(User.email == email).first()

    def count_admins(self):
        """Cuenta el número de administradores registrados."""
        count = self.db.query(User).filter(User.role == 'admin').count()
        logger.info(f"Número de administradores encontrados: {count}")
        return count

    def create_user(self, email: str, password: str, role: str = 'user'):
        logger.info(f"Creando nuevo usuario: {email}")
        hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        new_user = User(email=email, password=hashed.decode('utf-8'), role=role)
        self.db.add(new_user)
        self.db.commit()
        self.db.refresh(new_user)
        logger.info(f"Usuario creado con ID: {new_user.id}")
        return new_user

    def authenticate(self, email: str, password: str):
        """
        Verifica las credenciales del usuario.
        Retorna el objeto User si la autenticación es exitosa, de lo contrario None.
        """
        logger.info(f"Intentando autenticar usuario: {email}")
        user = self.get_user_by_email(email)
        if user and bcrypt.checkpw(password.encode('utf-8'), user.password.encode('utf-8')):
            logger.info(f"Autenticación exitosa para el usuario: {email}")
            return user
        logger.warning(f"Fallo en la autenticación del usuario: {email}")
        return None

    def update_user(self, user_id: int, email: str = None, password: str = None, role: str = None):
        user = self.get_user_by_id(user_id)
        if user:
            logger.info(f"Actualizando usuario con ID: {user_id}")
            if email:
                user.email = email
            if password:
                hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
                user.password = hashed.decode('utf-8')
            if role:
                user.role = role
            self.db.commit()
            self.db.refresh(user)
            logger.info(f"Usuario actualizado correctamente: {user_id}")
            return user
        logger.warning(f"Usuario no encontrado para actualizar: {user_id}")
        return None

    def delete_user(self, user_id: int):
        user = self.get_user_by_id(user_id)
        if user:
            logger.info(f"Eliminando usuario con ID: {user_id}")
            self.db.delete(user)
            self.db.commit()
            logger.info(f"Usuario eliminado correctamente: {user_id}")
            return user
        logger.warning(f"Usuario no encontrado para eliminar: {user_id}")
        return None
