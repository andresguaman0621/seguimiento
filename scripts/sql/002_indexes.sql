-- ============================================================
-- 002_indexes.sql
-- Índices para búsqueda rápida y regla de negocio a nivel de BD.
-- Ejecutar DESPUES de 001_schema.sql.
-- ============================================================

-- Login por cédula (la columna ya es UNIQUE, este índice acelera la búsqueda).
CREATE INDEX IF NOT EXISTS idx_usuarios_cedula
    ON usuarios (cedula);

-- Dashboard: filtrar actividades por estado (EN_CURSO).
CREATE INDEX IF NOT EXISTS idx_actividades_estado
    ON actividades (estado);

-- Historial: filtrar por usuario.
CREATE INDEX IF NOT EXISTS idx_actividades_usuario
    ON actividades (usuario_id);

-- Historial/reportes: filtrar y ordenar por fecha de inicio.
CREATE INDEX IF NOT EXISTS idx_actividades_inicio
    ON actividades (fecha_hora_inicio);

-- Regla de negocio garantizada por la BD:
-- un funcionario NO puede tener más de una actividad EN_CURSO a la vez.
CREATE UNIQUE INDEX IF NOT EXISTS ux_actividad_encurso
    ON actividades (usuario_id)
    WHERE estado = 'EN_CURSO';
