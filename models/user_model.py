import logging
from sqlalchemy import Column, Integer, String
from models.db import Base  # Importa la base común de tu proyecto

# Configuración básica de logs
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class User(Base):
    """
    Modelo de la tabla 'users' para el sistema de horarios.
    """
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(String(100), unique=True, index=True, nullable=False)
    password = Column(String(255), nullable=False)
    role = Column(String(20), default='user', nullable=False)

    def __init__(self, email, password, role='user'):
        self.email = email
        self.password = password
        self.role = role

    def __repr__(self):
        return f"<User(id={self.id}, email='{self.email}', role='{self.role}')>"
