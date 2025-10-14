import logging
from sqlalchemy.orm import Session
from repositories.horario_repository import HorarioRepository
from models.horario_model import Horario

# Configuración del logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

"""
Librerías utilizadas:
- repositories.horario_repository: Proporciona la clase HorarioRepository para gestionar los horarios en la base de datos.
- models.horario_model: Define el modelo Horario que representa la entidad de horario de un usuario.
- sqlalchemy.orm.Session: Permite manejar la sesión de la base de datos para realizar operaciones transaccionales.
"""

class HorarioService:
    """
    Capa de servicios para la gestión de horarios de usuarios.
    Esta clase centraliza la lógica de negocio asociada a los horarios, 
    garantizando validaciones y operaciones coherentes antes de interactuar con el repositorio.
    """

    def __init__(self, db_session: Session):
        """
        Inicializa el servicio con una sesión de base de datos y un repositorio de horarios.
        """
        self.repository = HorarioRepository(db_session)
        logger.info("Servicio de horarios inicializado")

    # =============================
    # Métodos de negocio principales
    # =============================

    def listar_horarios(self):
        """
        Recupera todos los horarios registrados.
        Útil para listados generales o vistas administrativas.
        """
        logger.info("Listando todos los horarios registrados")
        return self.repository.get_all_horarios()

    def obtener_horario(self, horario_id: int):
        """
        Busca un horario específico por su ID.
        """
        logger.info(f"Obteniendo horario con ID: {horario_id}")
        return self.repository.get_horario_by_id(horario_id)

    def crear_horario(self, user_id: int, dia: str, hora_inicio: str, hora_fin: str, actividad: str):
        """
        Crea un nuevo horario asociado a un usuario.
        Valida que la hora de inicio sea anterior a la hora final.
        """
        logger.info(f"Creando nuevo horario para usuario {user_id} - {dia} ({hora_inicio} a {hora_fin})")

        # Validación básica de horas
        if hora_inicio >= hora_fin:
            logger.warning("Hora de inicio no puede ser mayor o igual a la hora de fin")
            raise ValueError("La hora de inicio debe ser anterior a la hora de fin")

        # Aquí podrías agregar validaciones extra, como solapamientos:
        horarios_usuario = self.repository.get_horarios_by_user(user_id)
        for h in horarios_usuario:
            if h.dia == dia and not (hora_fin <= h.hora_inicio or hora_inicio >= h.hora_fin):
                logger.warning("Conflicto detectado: el horario se solapa con otro existente")
                raise ValueError("El horario se solapa con otro ya existente")

        return self.repository.create_horario(user_id, dia, hora_inicio, hora_fin, actividad)

    def actualizar_horario(self, horario_id: int, dia: str = None, hora_inicio: str = None, hora_fin: str = None, actividad: str = None):
        """
        Actualiza los datos de un horario existente.
        Valida la coherencia temporal antes de aplicar los cambios.
        """
        logger.info(f"Actualizando horario con ID: {horario_id}")

        # Validación de horas
        if hora_inicio and hora_fin and hora_inicio >= hora_fin:
            logger.warning("Hora de inicio no puede ser mayor o igual a la hora de fin (actualización)")
            raise ValueError("La hora de inicio debe ser anterior a la hora de fin")

        return self.repository.update_horario(horario_id, dia, hora_inicio, hora_fin, actividad)

    def eliminar_horario(self, horario_id: int):
        """
        Elimina un horario de la base de datos.
        """
        logger.info(f"Eliminando horario con ID: {horario_id}")
        return self.repository.delete_horario(horario_id)

    def listar_horarios_usuario(self, user_id: int):
        """
        Retorna todos los horarios asociados a un usuario específico.
        Es útil para mostrar el horario personal del usuario logueado.
        """
        logger.info(f"Listando horarios del usuario con ID: {user_id}")
        return self.repository.get_horarios_by_user(user_id)
