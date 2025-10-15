import bcrypt
from models.user_model import User

class UserService:
    def __init__(self, db):
        self.db = db

    def crear_usuario(self, email, password, role='user'):
        # Verificar si ya existe el usuario
        existing_user = self.db.query(User).filter_by(email=email).first()
        if existing_user:
            raise ValueError("El usuario ya existe")

        # Encriptar contraseña
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

        # Crear usuario
        user = User(email=email, password=hashed_password.decode('utf-8'), role=role)
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    def autenticar_usuario(self, email, password):
        user = self.db.query(User).filter_by(email=email).first()
        if not user:
            return None

        # Verificar contraseña
        if bcrypt.checkpw(password.encode('utf-8'), user.password.encode('utf-8')):
            return user
        return None
