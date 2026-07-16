"""Decoradores de autorizacion para las rutas de la API."""
from functools import wraps

import jwt
from flask import g, jsonify, request

from app.auth.jwt_utils import decodificar_token


def _extraer_token():
    encabezado = request.headers.get("Authorization", "")
    if encabezado.startswith("Bearer "):
        return encabezado[7:].strip()
    return None


def token_required(f):
    """Exige un JWT valido. Expone el usuario autenticado en `g.usuario`."""

    @wraps(f)
    def wrapper(*args, **kwargs):
        token = _extraer_token()
        if not token:
            return jsonify({"error": "Falta el token de autenticación"}), 401
        try:
            payload = decodificar_token(token)
        except jwt.ExpiredSignatureError:
            return jsonify({"error": "La sesión ha expirado"}), 401
        except jwt.PyJWTError:
            return jsonify({"error": "Token inválido"}), 401

        g.usuario = {
            "id": int(payload["sub"]),
            "nombre": payload.get("nombre"),
            "rol": payload.get("rol"),
        }
        return f(*args, **kwargs)

    return wrapper


def admin_required(f):
    """Exige un JWT valido y rol ADMIN."""

    @wraps(f)
    @token_required
    def wrapper(*args, **kwargs):
        if g.usuario.get("rol") != "ADMIN":
            return jsonify({"error": "Requiere permisos de administrador"}), 403
        return f(*args, **kwargs)

    return wrapper
