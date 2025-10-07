# config/jwt.py
import os
from datetime import timedelta

# Clave secreta para firmar tokens JWT
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "clave_secreta_temporal")

# Configuración básica de JWT
JWT_TOKEN_LOCATION = ["headers"]
JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
JWT_HEADER_NAME = "Authorization"
JWT_HEADER_TYPE = "Bearer"
