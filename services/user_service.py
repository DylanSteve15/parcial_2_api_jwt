import logging
from repositories.horario_repository import HorarioRepository
from sqlalchemy.orm import Session

# Configuración del logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class HorarioService:
    """
    Servicio de lógica de negocio para la gestión de horarios.
    Interactúa con el repositorio de horarios.
    """
    def __init__(self, db_session: Session):
        self.repository = HorarioRepository(db_session)
        logger.info("Servicio de horarios inicializado correctamente")

    def get_all_horarios(self):
        """Devuelve todos los horarios registrados."""
        logger.info("Listando todos los horarios")
        return self.repository.get_all_horarios()

    def get_horario_by_id(self, horario_id: int):
        """Obtiene un horario específico por su ID."""
        logger.info(f"Consultando horario con ID: {horario_id}")
        return self.repository.get_horario_by_id(horario_id)

    def create_horario(self, materia: str, dia: str, hora_inicio: str, hora_fin: str, aula: str):
        """Crea un nuevo horario validando los datos requeridos."""
        logger.info(f"Creando nuevo horario para la materia: {materia}")
        if not all([materia, dia, hora_inicio, hora_fin, aula]):
            logger.warning("Intento de creación de horario con datos incompletos")
            raise ValueError("Todos los campos (materia, día, hora inicio, hora fin y aula) son obligatorios.")
        return self.repository.create_horario(materia, dia, hora_inicio, hora_fin, aula)

    def update_horario(self, horario_id: int, materia: str = None, dia: str = None,
                       hora_inicio: str = None, hora_fin: str = None, aula: str = None):
        """Actualiza un horario existente."""
        logger.info(f"Actualizando horario con ID: {horario_id}")
        horario = self.repository.update_horario(horario_id, materia, dia, hora_inicio, hora_fin, aula)
        if not horario:
            logger.warning(f"No se encontró el horario con ID {horario_id} para actualizar")
            raise ValueError("Horario no encontrado.")
        return horario

    def delete_horario(self, horario_id: int):
        """Elimina un horario de la base de datos."""
        logger.info(f"Eliminando horario con ID: {horario_id}")
        horario = self.repository.delete_horario(horario_id)
        if not horario:
            logger.warning(f"No se encontró el horario con ID {horario_id} para eliminar")
            raise ValueError("Horario no encontrado.")
        return horario
