"""Configuración de la aplicación, cargada desde variables de entorno."""
import os

from dotenv import load_dotenv

load_dotenv()


class Config:
    # Base de datos (Turso / libSQL).
    TURSO_DATABASE_URL = os.getenv("TURSO_DATABASE_URL", "file:local.db")
    TURSO_AUTH_TOKEN = os.getenv("TURSO_AUTH_TOKEN", "")

    # JWT.
    JWT_SECRET = os.getenv("JWT_SECRET", "dev-secret-cambiar")
    JWT_EXP_HOURS = int(os.getenv("JWT_EXP_HOURS", "8"))
    JWT_ALGORITHM = "HS256"

    # Flask.
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-cambiar")
    DEBUG = os.getenv("FLASK_DEBUG", "0") == "1"
