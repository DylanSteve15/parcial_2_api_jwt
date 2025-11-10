import bcrypt
import logging
from models.user_model import User

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class UserService:
    def __init__(self, db):
        self.db = db

    def crear_usuario(self, email, password, role='user'):
        # Verificar si ya existe el usuario
        existing_user = self.db.query(User).filter_by(email=email).first()
        if existing_user:
            raise ValueError("El usuario ya existe")

        # Verificar si se intenta crear admin y ya existe uno
        if role == 'admin':
            existing_admin = self.db.query(User).filter_by(role='admin').first()
            if existing_admin:
                raise ValueError("Ya existe un administrador. Solo puede haber uno.")

        # Encriptar contraseña
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

        # Crear usuario
        user = User(email=email, password=hashed_password.decode('utf-8'), role=role)
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        logger.info(f"Usuario creado: {email} con rol {role}")
        return user

    def autenticar_usuario(self, email, password):
        user = self.db.query(User).filter_by(email=email).first()
        if not user:
            return None

        # Verificar contraseña
        if bcrypt.checkpw(password.encode('utf-8'), user.password.encode('utf-8')):
            return user
        return None

    def listar_usuarios(self):
        """Lista todos los usuarios"""
        logger.info("Listando todos los usuarios")
        return self.db.query(User).all()

    def obtener_usuario_por_id(self, user_id):
        """Obtiene un usuario por su ID"""
        logger.info(f"Obteniendo usuario por ID: {user_id}")
        return self.db.query(User).filter(User.id == user_id).first()

    def actualizar_usuario(self, user_id, email=None, password=None, role=None):
        """Actualiza un usuario existente"""
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            logger.warning(f"Usuario no encontrado para actualizar: {user_id}")
            return None

        logger.info(f"Actualizando usuario: {user_id}")
        
        # Verificar si se intenta cambiar a admin y ya existe uno
        if role == 'admin' and user.role != 'admin':
            existing_admin = self.db.query(User).filter_by(role='admin').first()
            if existing_admin:
                raise ValueError("Ya existe un administrador. Solo puede haber uno.")

        if email:
            # Verificar que el email no esté en uso por otro usuario
            existing_user = self.db.query(User).filter_by(email=email).first()
            if existing_user and existing_user.id != user_id:
                raise ValueError("El email ya está en uso por otro usuario")
            user.email = email

        if password:
            hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
            user.password = hashed_password.decode('utf-8')

        if role:
            user.role = role

        self.db.commit()
        self.db.refresh(user)
        logger.info(f"Usuario actualizado correctamente: {user_id}")
        return user

    def eliminar_usuario(self, user_id):
        """Elimina un usuario"""
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            logger.warning(f"Usuario no encontrado para eliminar: {user_id}")
            return None

        logger.info(f"Eliminando usuario: {user_id}")
        self.db.delete(user)
        self.db.commit()
        logger.info(f"Usuario eliminado correctamente: {user_id}")
        return user
