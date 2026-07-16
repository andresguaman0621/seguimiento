"""Endpoint de login sin contraseña (por cédula)."""
import time
from collections import defaultdict

from flask import Blueprint, jsonify, request

from app.auth.jwt_utils import generar_token
from app.repositories import usuarios_repo
from app.utils import cedula_formato_valido

bp = Blueprint("auth", __name__, url_prefix="/api/auth")

# Rate-limit básico en memoria: por IP, ventana deslizante.
_MAX_INTENTOS = 10
_VENTANA_SEG = 60
_intentos = defaultdict(list)


def _throttled(ip):
    ahora = time.time()
    recientes = [t for t in _intentos[ip] if ahora - t < _VENTANA_SEG]
    _intentos[ip] = recientes
    if len(recientes) >= _MAX_INTENTOS:
        return True
    _intentos[ip].append(ahora)
    return False


@bp.post("/login")
def login():
    if _throttled(request.remote_addr or "desconocido"):
        return jsonify({"error": "Demasiados intentos. Espere un momento."}), 429

    datos = request.get_json(silent=True) or {}
    cedula = str(datos.get("cedula", "")).strip()

    if not cedula_formato_valido(cedula):
        return jsonify({"error": "La cédula debe tener 10 dígitos numéricos"}), 400

    usuario = usuarios_repo.por_cedula(cedula)
    if usuario is None:
        return jsonify({"error": "Cédula no registrada"}), 401
    if not usuario["activo"]:
        return jsonify({"error": "El usuario está inactivo"}), 403

    token = generar_token(usuario)
    return jsonify(
        {
            "token": token,
            "usuario": {
                "id": usuario["id"],
                "nombre": usuario["nombre"],
                "rol": usuario["rol"],
            },
        }
    )
