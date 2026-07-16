-- ============================================================
-- 001_schema.sql
-- Esquema principal del sistema de seguimiento de actividades.
-- Ejecutar PRIMERO (antes de índices y seed).
-- ============================================================

PRAGMA foreign_keys = ON;

-- ------------------------------------------------------------
-- Usuarios: creados únicamente por el ADMIN (no hay registro público).
-- El login se realiza con la cédula (10 dígitos).
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS usuarios (
    id      INTEGER PRIMARY KEY AUTOINCREMENT,
    cedula  TEXT    NOT NULL UNIQUE,
    nombre  TEXT    NOT NULL,
    rol     TEXT    NOT NULL DEFAULT 'FUNCIONARIO'
                    CHECK (rol IN ('ADMIN', 'FUNCIONARIO')),
    activo  INTEGER NOT NULL DEFAULT 1
                    CHECK (activo IN (0, 1))
);

-- ------------------------------------------------------------
-- Tipos de actividad: catálogo manejado solo por el ADMIN.
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS tipos_actividad (
    id      INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre  TEXT    NOT NULL,
    activo  INTEGER NOT NULL DEFAULT 1
                    CHECK (activo IN (0, 1))
);

-- ------------------------------------------------------------
-- Actividades: cada registro es una "salida" de un funcionario.
-- Las fechas se almacenan en UTC en formato ISO-8601
-- (ej: 2026-07-15T14:30:00Z). El frontend las muestra en hora local.
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS actividades (
    id                 INTEGER PRIMARY KEY AUTOINCREMENT,
    usuario_id         INTEGER NOT NULL,
    tipo_actividad_id  INTEGER NOT NULL,
    comentario         TEXT    NOT NULL,
    estado             TEXT    NOT NULL DEFAULT 'EN_CURSO'
                               CHECK (estado IN ('EN_CURSO', 'FINALIZADA', 'CANCELADA')),
    fecha_hora_inicio  TEXT    NOT NULL,
    fecha_hora_fin     TEXT,
    FOREIGN KEY (usuario_id)        REFERENCES usuarios (id),
    FOREIGN KEY (tipo_actividad_id) REFERENCES tipos_actividad (id)
);
