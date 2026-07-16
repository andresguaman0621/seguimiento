"""Acceso a datos de actividades / salidas (SQL crudo)."""
from app import db

# SELECT base con los nombres desnormalizados que consume el frontend.
_SELECT_DETALLE = """
    SELECT a.id,
           a.usuario_id,
           u.nombre           AS usuario_nombre,
           u.cedula           AS usuario_cedula,
           a.tipo_actividad_id,
           t.nombre           AS tipo_nombre,
           a.comentario,
           a.estado,
           a.fecha_hora_inicio,
           a.fecha_hora_fin
    FROM actividades a
    JOIN usuarios u        ON u.id = a.usuario_id
    JOIN tipos_actividad t ON t.id = a.tipo_actividad_id
"""


def por_id(actividad_id):
    return db.query_one(_SELECT_DETALLE + " WHERE a.id = ?", [actividad_id])


def actual_de_usuario(usuario_id):
    """Actividad EN_CURSO del usuario (o None)."""
    return db.query_one(
        _SELECT_DETALLE + " WHERE a.usuario_id = ? AND a.estado = 'EN_CURSO'",
        [usuario_id],
    )


def crear(usuario_id, tipo_actividad_id, comentario, inicio_iso):
    result = db.execute(
        """INSERT INTO actividades
               (usuario_id, tipo_actividad_id, comentario, estado, fecha_hora_inicio)
           VALUES (?, ?, ?, 'EN_CURSO', ?)""",
        [usuario_id, tipo_actividad_id, comentario, inicio_iso],
    )
    return por_id(result.last_insert_rowid)


def cerrar(actividad_id, nuevo_estado, fin_iso):
    """Marca la actividad como FINALIZADA o CANCELADA y estampa la fecha de fin."""
    db.execute(
        "UPDATE actividades SET estado = ?, fecha_hora_fin = ? WHERE id = ?",
        [nuevo_estado, fin_iso, actividad_id],
    )
    return por_id(actividad_id)


def en_curso():
    """Dashboard admin: todas las actividades EN_CURSO, más recientes primero."""
    return db.query(
        _SELECT_DETALLE
        + " WHERE a.estado = 'EN_CURSO' ORDER BY a.fecha_hora_inicio DESC"
    )


def historial(desde=None, hasta=None, usuario_id=None, estado=None):
    """Historial/reportes con filtros opcionales por fecha, usuario y estado."""
    sql = _SELECT_DETALLE + " WHERE 1 = 1"
    params = []
    if desde:
        sql += " AND a.fecha_hora_inicio >= ?"
        params.append(desde)
    if hasta:
        sql += " AND a.fecha_hora_inicio <= ?"
        params.append(hasta)
    if usuario_id:
        sql += " AND a.usuario_id = ?"
        params.append(usuario_id)
    if estado:
        sql += " AND a.estado = ?"
        params.append(estado)
    sql += " ORDER BY a.fecha_hora_inicio DESC"
    return db.query(sql, params)
