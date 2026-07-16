"""CRU + soft delete de usuarios (solo ADMIN)."""
from flask import Blueprint, jsonify, request

from app.auth.decorators import admin_required
from app.db import LibsqlError
from app.repositories import usuarios_repo
from app.utils import cedula_formato_valido

bp = Blueprint("usuarios", __name__, url_prefix="/api/admin/usuarios")

_ROLES_VALIDOS = {"ADMIN", "FUNCIONARIO"}


@bp.get("")
@admin_required
def listar():
    return jsonify({"usuarios": usuarios_repo.listar(incluir_inactivos=True)})


@bp.post("")
@admin_required
def crear():
    datos = request.get_json(silent=True) or {}
    cedula = str(datos.get("cedula", "")).strip()
    nombre = str(datos.get("nombre", "")).strip()
    rol = str(datos.get("rol", "")).strip().upper()

    if not cedula_formato_valido(cedula):
        return jsonify({"error": "La cédula debe tener 10 dígitos numéricos"}), 400
    if not nombre:
        return jsonify({"error": "El nombre es obligatorio"}), 400
    if rol not in _ROLES_VALIDOS:
        return jsonify({"error": "Rol inválido"}), 400

    if usuarios_repo.por_cedula(cedula) is not None:
        return jsonify({"error": "Ya existe un usuario con esa cédula"}), 409

    try:
        usuario = usuarios_repo.crear(cedula, nombre, rol)
    except LibsqlError:
        return jsonify({"error": "Ya existe un usuario con esa cédula"}), 409

    return jsonify({"usuario": usuario}), 201


@bp.put("/<int:usuario_id>")
@admin_required
def actualizar(usuario_id):
    if usuarios_repo.por_id(usuario_id) is None:
        return jsonify({"error": "Usuario no encontrado"}), 404

    datos = request.get_json(silent=True) or {}
    nombre = str(datos.get("nombre", "")).strip()
    rol = str(datos.get("rol", "")).strip().upper()

    if not nombre:
        return jsonify({"error": "El nombre es obligatorio"}), 400
    if rol not in _ROLES_VALIDOS:
        return jsonify({"error": "Rol inválido"}), 400

    return jsonify({"usuario": usuarios_repo.actualizar(usuario_id, nombre, rol)})


@bp.patch("/<int:usuario_id>/estado")
@admin_required
def cambiar_estado(usuario_id):
    if usuarios_repo.por_id(usuario_id) is None:
        return jsonify({"error": "Usuario no encontrado"}), 404

    datos = request.get_json(silent=True) or {}
    activo = bool(datos.get("activo"))
    return jsonify({"usuario": usuarios_repo.cambiar_estado(usuario_id, activo)})
