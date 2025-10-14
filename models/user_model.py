# models/user_model.py
import logging
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from config.database import Base

# Configurar logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class User(Base):
    """
    Modelo que representa a los usuarios del sistema.
    Cada usuario puede tener múltiples horarios asociados.
    """
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    password = Column(String(255), nullable=False)
    email = Column(String(100), unique=True, nullable=True)

    # Relación con los horarios
    horarios = relationship("Horario", back_populates="usuario", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<User(username={self.username}, email={self.email})>"
