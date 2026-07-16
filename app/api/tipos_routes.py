"""CRU + soft delete del catálogo de tipos de actividad (solo ADMIN)."""
from flask import Blueprint, g, jsonify, request

from app.auth.decorators import admin_required, token_required
from app.repositories import tipos_repo

bp = Blueprint("tipos", __name__, url_prefix="/api/admin/tipos")


@bp.get("")
@token_required
def listar():
    """Lista tipos de actividad.

    Cualquier usuario autenticado puede pedir los tipos activos (para el dropdown
    del funcionario) con ?solo_activos=1. La lista completa (incl. inactivos) es
    solo para el ADMIN.
    """
    solo_activos = request.args.get("solo_activos") == "1"
    if not solo_activos and g.usuario.get("rol") != "ADMIN":
        return jsonify({"error": "Requiere permisos de administrador"}), 403
    return jsonify({"tipos": tipos_repo.listar(solo_activos=solo_activos)})


@bp.post("")
@admin_required
def crear():
    datos = request.get_json(silent=True) or {}
    nombre = str(datos.get("nombre", "")).strip()
    if not nombre:
        return jsonify({"error": "El nombre es obligatorio"}), 400
    return jsonify({"tipo": tipos_repo.crear(nombre)}), 201


@bp.put("/<int:tipo_id>")
@admin_required
def actualizar(tipo_id):
    if tipos_repo.por_id(tipo_id) is None:
        return jsonify({"error": "Tipo no encontrado"}), 404
    datos = request.get_json(silent=True) or {}
    nombre = str(datos.get("nombre", "")).strip()
    if not nombre:
        return jsonify({"error": "El nombre es obligatorio"}), 400
    return jsonify({"tipo": tipos_repo.actualizar(tipo_id, nombre)})


@bp.patch("/<int:tipo_id>/estado")
@admin_required
def cambiar_estado(tipo_id):
    if tipos_repo.por_id(tipo_id) is None:
        return jsonify({"error": "Tipo no encontrado"}), 404
    datos = request.get_json(silent=True) or {}
    activo = bool(datos.get("activo"))
    return jsonify({"tipo": tipos_repo.cambiar_estado(tipo_id, activo)})
