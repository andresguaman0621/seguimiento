"""Generación y validación de JSON Web Tokens."""
from datetime import datetime, timedelta, timezone

import jwt
from flask import current_app


def generar_token(usuario):
    """Genera un JWT firmado para un usuario.

    `usuario` es un dict con al menos: id, nombre, rol.
    """
    ahora = datetime.now(timezone.utc)
    payload = {
        "sub": str(usuario["id"]),
        "nombre": usuario["nombre"],
        "rol": usuario["rol"],
        "iat": ahora,
        "exp": ahora + timedelta(hours=current_app.config["JWT_EXP_HOURS"]),
    }
    return jwt.encode(
        payload,
        current_app.config["JWT_SECRET"],
        algorithm=current_app.config["JWT_ALGORITHM"],
    )


def decodificar_token(token):
    """Decodifica y valida un JWT. Lanza jwt.PyJWTError si es inválido/expirado."""
    return jwt.decode(
        token,
        current_app.config["JWT_SECRET"],
        algorithms=[current_app.config["JWT_ALGORITHM"]],
    )
