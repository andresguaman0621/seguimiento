"""Acceso a datos del catálogo de tipos de actividad (SQL crudo)."""
from app import db


def por_id(tipo_id):
    return db.query_one(
        "SELECT id, nombre, activo FROM tipos_actividad WHERE id = ?",
        [tipo_id],
    )


def listar(solo_activos=False):
    sql = "SELECT id, nombre, activo FROM tipos_actividad"
    if solo_activos:
        sql += " WHERE activo = 1"
    sql += " ORDER BY nombre COLLATE NOCASE"
    return db.query(sql)


def crear(nombre):
    result = db.execute(
        "INSERT INTO tipos_actividad (nombre, activo) VALUES (?, 1)",
        [nombre],
    )
    return por_id(result.last_insert_rowid)


def actualizar(tipo_id, nombre):
    db.execute(
        "UPDATE tipos_actividad SET nombre = ? WHERE id = ?",
        [nombre, tipo_id],
    )
    return por_id(tipo_id)


def cambiar_estado(tipo_id, activo):
    """Soft delete / reactivación del tipo de actividad."""
    db.execute(
        "UPDATE tipos_actividad SET activo = ? WHERE id = ?",
        [1 if activo else 0, tipo_id],
    )
    return por_id(tipo_id)
