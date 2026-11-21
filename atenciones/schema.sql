-- Modelo relacional de atenciones médicas (PostgreSQL)
-- Uso:  createdb atenciones
--       psql -d atenciones -f schema.sql

DROP TABLE IF EXISTS atencion;
DROP TABLE IF EXISTS paciente;
DROP TABLE IF EXISTS medico;

CREATE TABLE paciente (
    id_paciente SERIAL PRIMARY KEY,
    rut         VARCHAR(12)  NOT NULL UNIQUE,
    nombre      VARCHAR(100) NOT NULL,
    telefono    VARCHAR(20)
);

CREATE TABLE medico (
    id_medico    SERIAL PRIMARY KEY,
    nombre       VARCHAR(100) NOT NULL,
    especialidad VARCHAR(100) NOT NULL,
    telefono     VARCHAR(20)
);

CREATE TABLE atencion (
    id_atencion    SERIAL PRIMARY KEY,
    id_paciente    INTEGER NOT NULL REFERENCES paciente(id_paciente),
    id_medico      INTEGER NOT NULL REFERENCES medico(id_medico),
    fecha_atencion DATE    NOT NULL,
    fecha_alta     DATE,                    -- NULL = atención vigente
    diagnostico    TEXT,
    costo          INTEGER CHECK (costo >= 0), -- NULL = costo sin registrar
    CHECK (fecha_alta IS NULL OR fecha_alta >= fecha_atencion)
);
