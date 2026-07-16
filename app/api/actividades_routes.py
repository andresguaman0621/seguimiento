"""Endpoints de actividades / salidas para el funcionario autenticado."""
from flask import Blueprint, g, jsonify, request

from app.auth.decorators import token_required
from app.db import LibsqlError
from app.repositories import actividades_repo, tipos_repo
from app.utils import now_utc_iso

bp = Blueprint("actividades", __name__, url_prefix="/api/actividades")


@bp.get("/actual")
@token_required
def actual():
    """Devuelve la actividad EN_CURSO del usuario, o null."""
    return jsonify({"actividad": actividades_repo.actual_de_usuario(g.usuario["id"])})


@bp.post("")
@token_required
def crear():
    datos = request.get_json(silent=True) or {}
    tipo_id = datos.get("tipo_actividad_id")
    comentario = str(datos.get("comentario", "")).strip()

    if not tipo_id:
        return jsonify({"error": "Debe seleccionar un tipo de actividad"}), 400
    if not comentario:
        return jsonify({"error": "El comentario es obligatorio"}), 400

    tipo = tipos_repo.por_id(tipo_id)
    if tipo is None or not tipo["activo"]:
        return jsonify({"error": "Tipo de actividad inválido"}), 400

    if actividades_repo.actual_de_usuario(g.usuario["id"]) is not None:
        return jsonify({"error": "Ya tienes una actividad en curso"}), 409

    try:
        actividad = actividades_repo.crear(
            g.usuario["id"], tipo_id, comentario, now_utc_iso()
        )
    except LibsqlError:
        # Choque con el índice único parcial (carrera): ya existe una EN_CURSO.
        return jsonify({"error": "Ya tienes una actividad en curso"}), 409

    return jsonify({"actividad": actividad}), 201


def _cerrar(actividad_id, nuevo_estado):
    actividad = actividades_repo.por_id(actividad_id)
    if actividad is None:
        return jsonify({"error": "Actividad no encontrada"}), 404
    if actividad["usuario_id"] != g.usuario["id"]:
        return jsonify({"error": "No puedes modificar esta actividad"}), 403
    if actividad["estado"] != "EN_CURSO":
        return jsonify({"error": "La actividad ya no está en curso"}), 409

    actualizada = actividades_repo.cerrar(actividad_id, nuevo_estado, now_utc_iso())
    return jsonify({"actividad": actualizada})


@bp.patch("/<int:actividad_id>/finalizar")
@token_required
def finalizar(actividad_id):
    return _cerrar(actividad_id, "FINALIZADA")


@bp.patch("/<int:actividad_id>/cancelar")
@token_required
def cancelar(actividad_id):
    return _cerrar(actividad_id, "CANCELADA")
