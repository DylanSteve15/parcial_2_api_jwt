#repositories/horario_repository
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

    def create_horario(self, materia: str, docente: str, dia: str, hora_inicio: str, hora_fin: str, salon: str, user_id: int = None):
        """
        Crea un nuevo horario en la base de datos.
        Convierte las horas de texto a formato datetime si es necesario.
        """
        logger.info(f"Creando horario para la materia: {materia}")
        try:
            # Intentar parsear las horas - el input type="time" devuelve formato HH:MM
            from datetime import datetime
            # Si viene en formato HH:MM, usar datetime.strptime
            if len(hora_inicio) == 5 and ':' in hora_inicio:  # Formato HH:MM
                hora_inicio_parsed = datetime.strptime(hora_inicio, '%H:%M').time()
            else:
                hora_inicio_parsed = parser.parse(hora_inicio).time()
            
            if len(hora_fin) == 5 and ':' in hora_fin:  # Formato HH:MM
                hora_fin_parsed = datetime.strptime(hora_fin, '%H:%M').time()
            else:
                hora_fin_parsed = parser.parse(hora_fin).time()
        except Exception as e:
            logger.warning(f"Error al convertir las horas: {str(e)}, intentando parsear con dateutil")
            try:
                hora_inicio_parsed = parser.parse(hora_inicio).time()
                hora_fin_parsed = parser.parse(hora_fin).time()
            except Exception as e2:
                logger.error(f"Error definitivo al convertir las horas: {str(e2)}")
                raise ValueError(f"Formato de hora inválido: {hora_inicio} o {hora_fin}")

        # Validar que el user_id existe si se proporciona
        if user_id is not None:
            from models.user_model import User
            user_exists = self.db.query(User).filter(User.id == user_id).first()
            if not user_exists:
                logger.warning(f"Usuario con ID {user_id} no existe, se creará horario sin usuario asignado")
                user_id = None

        nuevo_horario = Horario(
            materia=materia,
            docente=docente,
            dia=dia,
            hora_inicio=hora_inicio_parsed,
            hora_fin=hora_fin_parsed,
            salon=salon,
            user_id=user_id
        )
        try:
            self.db.add(nuevo_horario)
            self.db.commit()
            self.db.refresh(nuevo_horario)
            logger.info(f"Horario creado correctamente con ID: {nuevo_horario.id}")
            return nuevo_horario
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error al guardar horario en la base de datos: {str(e)}")
            raise

    def update_horario(self, horario_id: int, materia: str = None, docente: str = None, dia: str = None,
                       hora_inicio: str = None, hora_fin: str = None, salon: str = None, user_id: int = None):
        """Actualiza un horario existente en la base de datos."""
        horario = self.get_horario_by_id(horario_id)
        if horario:
            logger.info(f"Actualizando horario con ID: {horario_id}")
            if materia:
                horario.materia = materia
            if docente:
                horario.docente = docente
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
            if salon:
                horario.salon = salon
            if user_id is not None:
                horario.user_id = user_id
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
