"""Acceso a datos de usuarios (SQL crudo)."""
from app import db


def por_cedula(cedula):
    """Devuelve el usuario con esa cédula, o None."""
    return db.query_one(
        "SELECT id, cedula, nombre, rol, activo FROM usuarios WHERE cedula = ?",
        [cedula],
    )


def por_id(usuario_id):
    return db.query_one(
        "SELECT id, cedula, nombre, rol, activo FROM usuarios WHERE id = ?",
        [usuario_id],
    )


def listar(incluir_inactivos=True):
    """Lista usuarios ordenados por nombre. Por defecto incluye inactivos (vista admin)."""
    sql = "SELECT id, cedula, nombre, rol, activo FROM usuarios"
    if not incluir_inactivos:
        sql += " WHERE activo = 1"
    sql += " ORDER BY nombre COLLATE NOCASE"
    return db.query(sql)


def crear(cedula, nombre, rol):
    result = db.execute(
        "INSERT INTO usuarios (cedula, nombre, rol, activo) VALUES (?, ?, ?, 1)",
        [cedula, nombre, rol],
    )
    return por_id(result.last_insert_rowid)


def actualizar(usuario_id, nombre, rol):
    db.execute(
        "UPDATE usuarios SET nombre = ?, rol = ? WHERE id = ?",
        [nombre, rol, usuario_id],
    )
    return por_id(usuario_id)


def cambiar_estado(usuario_id, activo):
    """Soft delete / reactivación: activo = 0 o 1."""
    db.execute(
        "UPDATE usuarios SET activo = ? WHERE id = ?",
        [1 if activo else 0, usuario_id],
    )
    return por_id(usuario_id)
