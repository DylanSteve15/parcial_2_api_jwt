# config/database.py
import os
import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.exc import OperationalError
from dotenv import load_dotenv

# Configurar logs
logging.basicConfig(level=logging.INFO)

# Cargar variables de entorno desde .env
load_dotenv()

# URIs de base de datos
RAILWAY_DB_URI = os.getenv('RAILWAY_DB_URI')  # Ejemplo: mysql+pymysql://user:pass@host/db
SQLITE_URI = 'sqlite:///horarios_local.db'

# Crear instancia de Base
Base = declarative_base()

def get_engine():
    """
    Intenta conectar a Railway (si existe variable de entorno). 
    Si falla, usa SQLite local como respaldo.
    """
    if RAILWAY_DB_URI:
        try:
            engine = create_engine(RAILWAY_DB_URI, echo=False)
            conn = engine.connect()
            conn.close()
            logging.info('✅ Conexión a Railway exitosa.')
            return engine
        except OperationalError:
            logging.warning('⚠️ No se pudo conectar a Railway. Usando SQLite local.')

    logging.info('🗄️ Usando base de datos local SQLite.')
    return create_engine(SQLITE_URI, echo=False)

# Crear motor y sesión
engine = get_engine()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    """
    Crea todas las tablas definidas en los modelos.
    """
    import models.user_model
    import models.horario_model
    Base.metadata.create_all(bind=engine)
    logging.info('📦 Tablas creadas o verificadas correctamente.')

def get_db_session():
    """
    Retorna una sesión lista para usar en controladores o servicios.
    """
    return SessionLocal()
