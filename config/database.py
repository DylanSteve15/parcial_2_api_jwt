import os
import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import OperationalError
from dotenv import load_dotenv
from models import Base  # Importa la base declarativa de tus modelos

# Configurar logging
logging.basicConfig(level=logging.INFO)

# Cargar variables del entorno (.env)
load_dotenv()

# URI principal y de respaldo
MYSQL_URI = os.getenv("MYSQL_URI")  # Ejemplo: mysql+pymysql://user:password@host/db
SQLITE_URI = "sqlite:///horarios_local.db"

def get_engine():
    """
    Intenta crear una conexión con MySQL.
    Si falla, usa SQLite como respaldo local.
    """
    if MYSQL_URI:
        try:
            engine = create_engine(MYSQL_URI, echo=True)
            # Prueba de conexión
            conn = engine.connect()
            conn.close()
            logging.info("✅ Conexión a MySQL exitosa.")
            return engine
        except OperationalError:
            logging.warning("⚠️ No se pudo conectar a MySQL. Usando SQLite local.")
    # Si MySQL falla o no existe, usa SQLite
    engine = create_engine(SQLITE_URI, echo=True)
    return engine

# Crear motor y sesión
engine = get_engine()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Crear las tablas definidas en los modelos (si no existen)
Base.metadata.create_all(bind=engine)

def get_db_session():
    """
    Retorna una nueva sesión de base de datos.
    Se usa dentro de los servicios o controladores.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
