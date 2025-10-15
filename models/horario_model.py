#models/horario_model
import logging
from sqlalchemy import Column, Integer, String, Time, Date
from models.db import Base

# Configuración de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Horario(Base):
    """
    Modelo de la tabla 'horarios' para el sistema de gestión de horarios.
    """
    __tablename__ = 'horarios'

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    materia = Column(String(255), nullable=False)
    docente = Column(String(255), nullable=False)
    dia = Column(String(50), nullable=False)
    hora_inicio = Column(Time, nullable=False)
    hora_fin = Column(Time, nullable=False)
    salon = Column(String(100), nullable=True)

    def __init__(self, materia, docente, dia, hora_inicio, hora_fin, salon=None):
        self.materia = materia
        self.docente = docente
        self.dia = dia
        self.hora_inicio = hora_inicio
        self.hora_fin = hora_fin
        self.salon = salon

    def __repr__(self):
        return (
            f"<Horario(id={self.id}, materia='{self.materia}', docente='{self.docente}', "
            f"dia='{self.dia}', hora_inicio='{self.hora_inicio}', hora_fin='{self.hora_fin}', "
            f"salon='{self.salon}')>"
        )
