"""Capa de acceso a datos: cliente libSQL (Turso) por request.

Se usa SQL crudo con placeholders posicionales (`?`). El cliente se crea una vez
por request (guardado en `flask.g`) y se cierra en el teardown del contexto.
"""
import libsql_client
from flask import current_app, g

# Se re-exporta para que los repositorios puedan capturar errores de la BD
# (por ejemplo, violaciones del índice único parcial de actividad EN_CURSO).
LibsqlError = libsql_client.LibsqlError


def get_client():
    """Devuelve el cliente libSQL asociado al request actual (lo crea si no existe)."""
    if "db_client" not in g:
        url = current_app.config["TURSO_DATABASE_URL"]
        token = current_app.config.get("TURSO_AUTH_TOKEN") or None
        g.db_client = libsql_client.create_client_sync(url, auth_token=token)
    return g.db_client


def close_client(exc=None):  # noqa: ARG001 - firma requerida por teardown
    """Cierra el cliente libSQL al finalizar el request."""
    client = g.pop("db_client", None)
    if client is not None:
        client.close()


def _rows_to_dicts(result_set):
    cols = result_set.columns
    return [dict(zip(cols, row)) for row in result_set.rows]


def query(sql, params=None):
    """Ejecuta un SELECT y devuelve una lista de diccionarios."""
    result_set = get_client().execute(sql, params or [])
    return _rows_to_dicts(result_set)


def query_one(sql, params=None):
    """Ejecuta un SELECT y devuelve el primer registro (o None)."""
    rows = query(sql, params)
    return rows[0] if rows else None


def execute(sql, params=None):
    """Ejecuta un INSERT/UPDATE/DELETE.

    Devuelve el ResultSet, que expone `last_insert_rowid` y `rows_affected`.
    """
    return get_client().execute(sql, params or [])


def init_app(app):
    """Registra el cierre del cliente en el teardown de la app."""
    app.teardown_appcontext(close_client)
