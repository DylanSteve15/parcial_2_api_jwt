import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
from models.users_model import User
from sqlalchemy.orm import Session

class UserRepository:
    """
    Repositorio para la gestión de usuarios en la base de datos.
    Proporciona métodos para crear, consultar, actualizar y eliminar usuarios.
    """

    def __init__(self, db_session: Session):
        self.db = db_session

    def get_all_users(self):
        """
        Recupera todos los usuarios almacenados en la base de datos.
        Utiliza una consulta ORM para obtener todas las instancias de la clase User,
        permitiendo así listar todos los usuarios registrados en el sistema. Es útil para
        mostrar catálogos, listados generales o para operaciones que requieran acceder
        a la colección completa de usuarios.
        """
        #SELECT * FROM users;
        logger.info("Obteniendo todos los usuarios desde el repositorio")
        return self.db.query(User).all()

    def get_user_by_id(self, user_id: int):
        """
        Busca y retorna un usuario específico según su identificador único (ID).
        Realiza una consulta filtrando por el campo 'id' de la tabla User. Es útil
        para obtener detalles de un usuario concreto, por ejemplo, al consultar su
        información o al realizar operaciones de actualización o eliminación.
        Devuelve la instancia de User si existe, o None si no se encuentra.
        """
        #SELECT * FROM users WHERE id = user_id;
        logger.info(f"Buscando usuario por ID: {user_id}")
        return self.db.query(User).filter(User.id == user_id).first()

    def create_user(self, username: str, password: str):
        """
        Crea y almacena un nuevo usuario en la base de datos.
        Recibe el nombre de usuario y la contraseña como parámetros, instancia un nuevo objeto User
        y lo agrega a la sesión de la base de datos. Tras confirmar la transacción,
        retorna el nuevo usuario creado, incluyendo su ID asignado automáticamente.
        Es útil para registrar nuevos usuarios en el sistema.
        """
        #INSERT INTO users (username, password) VALUES (username, password);
        logger.info(f"Creando usuario: {username}")
        new_user = User(username=username, password=password)
        self.db.add(new_user)
        self.db.commit()
        self.db.refresh(new_user)
        return new_user
    
    def update_user(self, user_id: int, username: str = None, password: str = None):
        """
        Actualiza la información de un usuario existente en la base de datos.
        Permite modificar el nombre de usuario y/o la contraseña del usuario identificado por su ID.
        Si el usuario existe y se proporcionan nuevos valores, se actualiza el registro y se guarda
        el cambio en la base de datos. Devuelve la instancia del usuario actualizado
        o None si no se encuentra el usuario. Es útil para mantener actualizada la
        información de los usuarios.
        """
        user = self.get_user_by_id(user_id)
        if user:
            logger.info(f"Actualizando usuario: {user_id}")
            if username:
                user.username = username
            if password:
                user.password = password
            self.db.commit()
            self.db.refresh(user)
            return user
        logger.warning(f"Usuario no encontrado para actualizar: {user_id}")
        return None
    
    def delete_user(self, user_id: int):
        """
        Elimina un usuario de la base de datos según su identificador único (ID).
        Busca el usuario correspondiente y, si existe, lo elimina de la base de datos y
        confirma la transacción. Devuelve la instancia del usuario eliminado o None si
        no se encuentra el usuario. Es útil para gestionar la eliminación de usuarios
        que ya no son necesarios en el sistema.
        """
        user = self.get_user_by_id(user_id)
        if user:
            logger.info(f"Eliminando usuario: {user_id}")
            self.db.delete(user)
            self.db.commit()
            return user
        logger.warning(f"Usuario no encontrado para eliminar: {user_id}")
        return None