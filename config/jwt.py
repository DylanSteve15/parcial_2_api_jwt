# config/jwt.py
import os
import secrets
import logging

logger = logging.getLogger(__name__)

JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
if not JWT_SECRET_KEY:
    logger.warning("JWT_SECRET_KEY no encontrada en variables de entorno, generando una nueva...")
    JWT_SECRET_KEY = secrets.token_hex(32)
    logger.info("JWT_SECRET_KEY generada automáticamente")

JWT_TOKEN_LOCATION = ["headers"]
JWT_ACCESS_TOKEN_EXPIRES = 3600
JWT_HEADER_NAME = "Authorization"
JWT_HEADER_TYPE = "Bearer"