-- ============================================================
-- 003_seed_admin.sql
-- Datos iniciales para arrancar el sistema.
-- Ejecutar DESPUES de 001_schema.sql y 002_indexes.sql.
--
-- IMPORTANTE: cambia la cédula '0000000000' por la cédula real
-- del administrador (jefatura) antes de ejecutar este script.
-- ============================================================

-- Administrador inicial (jefatura).
INSERT OR IGNORE INTO usuarios (cedula, nombre, rol, activo)
VALUES ('1718593344', 'Administrador', 'ADMIN', 1);

-- Un funcionario de ejemplo (opcional, puedes eliminarlo).
INSERT OR IGNORE INTO usuarios (cedula, nombre, rol, activo)
VALUES ('1111111111', 'Funcionario Demo', 'FUNCIONARIO', 1);

-- Catálogo inicial de tipos de actividad.
INSERT OR IGNORE INTO tipos_actividad (nombre, activo) VALUES ('Reunión', 1);
INSERT OR IGNORE INTO tipos_actividad (nombre, activo) VALUES ('Capacitación', 1);
INSERT OR IGNORE INTO tipos_actividad (nombre, activo) VALUES ('Soporte', 1);