-- ============================================================================
-- proyecto-propiedades · Schema v1 (idempotente)
-- ============================================================================

USE propiedades_db;

CREATE TABLE IF NOT EXISTS propiedades (
  id                INT AUTO_INCREMENT PRIMARY KEY,
  titulo            VARCHAR(180)    NOT NULL,
  descripcion       TEXT            NULL,
  tipo              ENUM('casa','departamento','terreno','oficina','local')
                                    NOT NULL,
  precio            DECIMAL(12, 2)  NOT NULL,
  habitaciones      INT             NULL,
  banos             INT             NULL,
  area_m2           DECIMAL(10, 2)  NULL,
  ubicacion         VARCHAR(160)    NOT NULL,
  fecha_publicacion DATE            NOT NULL,
  UNIQUE KEY uq_titulo_ubicacion (titulo, ubicacion),
  INDEX idx_tipo                    (tipo),
  INDEX idx_precio                  (precio),
  INDEX idx_ubicacion               (ubicacion),
  INDEX idx_fecha_publicacion       (fecha_publicacion),
  INDEX idx_habitaciones_banos      (habitaciones, banos),
  INDEX idx_tipo_precio             (tipo, precio),
  FULLTEXT INDEX ft_search          (titulo, descripcion, ubicacion),
  CONSTRAINT chk_precio_positivo    CHECK (precio >= 0),
  CONSTRAINT chk_habitaciones_pos   CHECK (habitaciones IS NULL OR habitaciones >= 0),
  CONSTRAINT chk_banos_pos          CHECK (banos IS NULL OR banos >= 0),
  CONSTRAINT chk_area_pos           CHECK (area_m2 IS NULL OR area_m2 >= 0)
) ENGINE=InnoDB
  DEFAULT CHARSET=utf8mb4
  COLLATE=utf8mb4_unicode_ci;

-- ============================================================================
-- Hardening opcional · Usuario read-only (ADR-013)
-- Baseline (PDF): backend usa `appuser` con full grants.
-- Hardening:     activable via docker-compose.override.yml cambiando DB_USER.
-- ============================================================================

CREATE USER IF NOT EXISTS 'appuser_ro'@'%' IDENTIFIED BY 'apppass_ro';
GRANT SELECT ON propiedades_db.propiedades TO 'appuser_ro'@'%';
FLUSH PRIVILEGES;
