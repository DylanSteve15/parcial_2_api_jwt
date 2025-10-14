# repositories/horario_repository.py

import logging
from sqlalchemy.orm import Session
from models.horario_model import Horario

# Configurar logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class HorarioRepository:
    """
    Repositorio para la gestión de los horarios en la base de datos.
    Permite crear, consultar, actualizar y eliminar horarios, así como filtrar por usuario.
    """

    def __init__(self, db_session: Session):
        self.db = db_session

    # -------------------- 🔍 READ --------------------
    def get_all_horarios(self):
        """
        Retorna todos los horarios existentes en la base de datos.
        Ideal para listados administrativos o de depuración.
        """
        logger.info("Obteniendo todos los horarios.")
        return self.db.query(Horario).all()

    def get_horarios_by_user(self, user_id: int):
        """
        Retorna todos los horarios asociados a un usuario específico.
        Esto permite mostrar al usuario logueado únicamente sus horarios.
        """
        logger.info(f"Obteniendo horarios del usuario con ID: {user_id}")
        return self.db.query(Horario).filter(Horario.user_id == user_id).all()

    def get_horario_by_id(self, horario_id: int):
        """
        Retorna un horario específico según su ID.
        """
        logger.info(f"Buscando horario por ID: {horario_id}")
        return self.db.query(Horario).filter(Horario.id == horario_id).first()

    # -------------------- ✏️ CREATE --------------------
    def create_horario(self, user_id: int, dia: str, hora_inicio, hora_fin, actividad: str):
        """
        Crea y guarda un nuevo horario en la base de datos.
        Los campos de hora deben ser objetos datetime.time o cadenas en formato HH:MM:SS.
        """
        logger.info(f"Creando nuevo horario para usuario {user_id}: {actividad} ({dia})")
        nuevo_horario = Horario(
            user_id=user_id,
            dia=dia,
            hora_inicio=hora_inicio,
            hora_fin=hora_fin,
            actividad=actividad
        )
        self.db.add(nuevo_horario)
        self.db.commit()
        self.db.refresh(nuevo_horario)
        return nuevo_horario

    # -------------------- 🧩 UPDATE --------------------
    def update_horario(self, horario_id: int, dia: str = None, hora_inicio=None, hora_fin=None, actividad: str = None):
        """
        Actualiza los datos de un horario existente.
        Solo actualiza los campos que se proporcionen.
        """
        horario = self.get_horario_by_id(horario_id)
        if not horario:
            logger.warning(f"Horario con ID {horario_id} no encontrado.")
            return None

        logger.info(f"Actualizando horario ID {horario_id}.")
        if dia:
            horario.dia = dia
        if hora_inicio:
            horario.hora_inicio = hora_inicio
        if hora_fin:
            horario.hora_fin = hora_fin
        if actividad:
            horario.actividad = actividad

        self.db.commit()
        self.db.refresh(horario)
        return horario

    # -------------------- ❌ DELETE --------------------
    def delete_horario(self, horario_id: int):
        """
        Elimina un horario por su identificador único.
        """
        horario = self.get_horario_by_id(horario_id)
        if not horario:
            logger.warning(f"Horario con ID {horario_id} no encontrado para eliminar.")
            return None

        logger.info(f"Eliminando horario ID {horario_id}.")
        self.db.delete(horario)
        self.db.commit()
        return horario
