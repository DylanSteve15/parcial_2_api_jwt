import logging
from sqlalchemy.orm import Session
from models.horario_model import Horario
from dateutil import parser

# Configuración de logs
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class HorarioRepository:
    """
    Repositorio encargado de manejar las operaciones CRUD del modelo Horario.
    """
    def __init__(self, db_session: Session):
        self.db = db_session

    def get_all_horarios(self):
        """Obtiene todos los registros de horarios."""
        logger.info("Obteniendo todos los horarios desde el repositorio.")
        return self.db.query(Horario).all()

    def get_horario_by_id(self, horario_id: int):
        """Busca un horario específico por su ID."""
        logger.info(f"Buscando horario por ID: {horario_id}")
        return self.db.query(Horario).filter(Horario.id == horario_id).first()

    def create_horario(self, materia: str, dia: str, hora_inicio: str, hora_fin: str, aula: str):
        """
        Crea un nuevo horario en la base de datos.
        Convierte las horas de texto a formato datetime si es necesario.
        """
        logger.info(f"Creando horario para la materia: {materia}")
        try:
            hora_inicio_parsed = parser.parse(hora_inicio).time()
            hora_fin_parsed = parser.parse(hora_fin).time()
        except Exception:
            logger.warning("Error al convertir las horas, se almacenarán como texto.")
            hora_inicio_parsed = hora_inicio
            hora_fin_parsed = hora_fin

        nuevo_horario = Horario(
            materia=materia,
            dia=dia,
            hora_inicio=hora_inicio_parsed,
            hora_fin=hora_fin_parsed,
            aula=aula
        )
        self.db.add(nuevo_horario)
        self.db.commit()
        self.db.refresh(nuevo_horario)
        logger.info(f"Horario creado correctamente con ID: {nuevo_horario.id}")
        return nuevo_horario

    def update_horario(self, horario_id: int, materia: str = None, dia: str = None,
                       hora_inicio: str = None, hora_fin: str = None, aula: str = None):
        """Actualiza un horario existente en la base de datos."""
        horario = self.get_horario_by_id(horario_id)
        if horario:
            logger.info(f"Actualizando horario con ID: {horario_id}")
            if materia:
                horario.materia = materia
            if dia:
                horario.dia = dia
            if hora_inicio:
                try:
                    horario.hora_inicio = parser.parse(hora_inicio).time()
                except Exception:
                    horario.hora_inicio = hora_inicio
            if hora_fin:
                try:
                    horario.hora_fin = parser.parse(hora_fin).time()
                except Exception:
                    horario.hora_fin = hora_fin
            if aula:
                horario.aula = aula
            self.db.commit()
            self.db.refresh(horario)
            logger.info(f"Horario actualizado correctamente: {horario_id}")
            return horario
        logger.warning(f"Horario no encontrado para actualizar: {horario_id}")
        return None

    def delete_horario(self, horario_id: int):
        """Elimina un horario de la base de datos."""
        horario = self.get_horario_by_id(horario_id)
        if horario:
            logger.info(f"Eliminando horario con ID: {horario_id}")
            self.db.delete(horario)
            self.db.commit()
            logger.info(f"Horario eliminado correctamente: {horario_id}")
            return horario
        logger.warning(f"Horario no encontrado para eliminar: {horario_id}")
        return None
