# models/horario_model.py
import logging
from sqlalchemy import Column, Integer, String, ForeignKey, Time, Date
from sqlalchemy.orm import relationship
from config.database import Base

# Configurar logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Horario(Base):
    """
    Modelo que representa los horarios registrados por los usuarios.
    Cada horario pertenece a un usuario específico.
    """
    __tablename__ = "horarios"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    dia = Column(String(20), nullable=False)          # Ejemplo: 'Lunes', 'Martes', etc.
    hora_inicio = Column(Time, nullable=False)        # Ejemplo: 08:00:00
    hora_fin = Column(Time, nullable=False)           # Ejemplo: 12:00:00
    actividad = Column(String(100), nullable=False)   # Ejemplo: 'Clase de programación', 'Reunión'

    # Relación inversa
    usuario = relationship("User", back_populates="horarios")

    def __repr__(self):
        return f"<Horario(dia={self.dia}, actividad={self.actividad}, usuario_id={self.user_id})>"
