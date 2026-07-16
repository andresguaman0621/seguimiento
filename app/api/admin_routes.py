"""Endpoints de reportes para el ADMIN: dashboard e historial."""
from flask import Blueprint, jsonify, request

from app.auth.decorators import admin_required
from app.repositories import actividades_repo

bp = Blueprint("admin", __name__, url_prefix="/api/admin")

_ESTADOS_VALIDOS = {"EN_CURSO", "FINALIZADA", "CANCELADA"}


@bp.get("/dashboard")
@admin_required
def dashboard():
    """Funcionarios actualmente fuera de la oficina (estado EN_CURSO)."""
    return jsonify({"actividades": actividades_repo.en_curso()})


@bp.get("/actividades")
@admin_required
def historial():
    """Historial filtrable por fecha (desde/hasta), usuario y estado.

    `desde` y `hasta` se esperan como ISO-8601 UTC. Para filtrar por día completo,
    el frontend envía rangos inclusivos.
    """
    usuario_id = request.args.get("usuario_id", type=int)
    estado = request.args.get("estado")
    if estado and estado not in _ESTADOS_VALIDOS:
        return jsonify({"error": "Estado inválido"}), 400

    actividades = actividades_repo.historial(
        desde=request.args.get("desde") or None,
        hasta=request.args.get("hasta") or None,
        usuario_id=usuario_id,
        estado=estado or None,
    )
    return jsonify({"actividades": actividades})
