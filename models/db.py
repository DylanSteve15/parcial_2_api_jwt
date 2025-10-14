# models/db.py
"""
Módulo central de inicialización de la base de datos.
Permite obtener sesiones y crear todas las tablas del modelo.
"""

import logging
from config.database import Base, engine, SessionLocal, init_db

# Configuración básica del logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_tables():
    """
    Crea todas las tablas definidas en los modelos.
    """
    try:
        init_db()
        logger.info("✅ Tablas creadas o actualizadas correctamente.")
    except Exception as e:
        logger.error(f"❌ Error al crear las tablas: {e}")

def get_session():
    """
    Retorna una nueva sesión de base de datos para operaciones CRUD.
    Se debe cerrar con session.close() cuando se termina de usar.
    """
    try:
        session = SessionLocal()
        logger.debug("🧩 Sesión de base de datos creada.")
        return session
    except Exception as e:
        logger.error(f"❌ Error al crear la sesión: {e}")
        raise e

# Si se ejecuta directamente este archivo, inicializa la BD.
if __name__ == "__main__":
    create_tables()
    logger.info("🚀 Base de datos inicializada correctamente.")

