#services/horario_service
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

from repositories.horario_repository import HorarioRepository
from models.horario_model import Horario
from sqlalchemy.orm import Session

class HorarioService:
    def __init__(self, db_session: Session):
        self.repository = HorarioRepository(db_session)
        logger.info("Servicio de horarios inicializado")

    def listar_horarios(self):
        logger.info("Listando todos los horarios")
        return self.repository.get_all_horarios()

    def obtener_horario(self, horario_id: int):
        logger.info(f"Obteniendo horario por ID: {horario_id}")
        return self.repository.get_horario_by_id(horario_id)

    def crear_horario(self, materia: str, docente: str, dia: str, hora_inicio: str, hora_fin: str, salon: str, user_id: int = None):
        logger.info(f"Creando horario para la materia: {materia}")
        return self.repository.create_horario(materia, docente, dia, hora_inicio, hora_fin, salon, user_id)

    def actualizar_horario(self, horario_id: int, materia: str = None, docente: str = None, dia: str = None, 
                           hora_inicio: str = None, hora_fin: str = None, salon: str = None, user_id: int = None):
        logger.info(f"Actualizando horario: {horario_id}")
        return self.repository.update_horario(horario_id, materia, docente, dia, hora_inicio, hora_fin, salon, user_id)

    def eliminar_horario(self, horario_id: int):
        logger.info(f"Eliminando horario: {horario_id}")
        return self.repository.delete_horario(horario_id)
