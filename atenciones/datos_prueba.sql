-- Datos de prueba (ejecutar después de schema.sql)
INSERT INTO paciente (rut, nombre, telefono) VALUES
 ('12.345.678-5', 'Ana Pérez',    '+56911111111'),
 ('9.876.543-2',  'Luis Soto',    '+56922222222'),
 ('15.555.444-K', 'María Rojas',  '+56933333333');

INSERT INTO medico (nombre, especialidad, telefono) VALUES
 ('Dr. Carlos Vega',  'Cardiología', '+56944444444'),
 ('Dra. Elena Ruiz',  'Pediatría',   '+56955555555'),
 ('Dr. Pablo Núñez',  'Traumatología','+56966666666');

-- Con alta (NO deben aparecer en la consulta de vigentes)
INSERT INTO atencion (id_paciente, id_medico, fecha_atencion, fecha_alta, diagnostico, costo) VALUES
 (1, 1, '2026-10-01', '2026-10-05', 'Arritmia leve', 45000),
 (2, 2, '2026-10-10', '2026-10-12', 'Control sano',  25000);

-- Sin alta (vigentes)
INSERT INTO atencion (id_paciente, id_medico, fecha_atencion, fecha_alta, diagnostico, costo) VALUES
 (1, 3, '2026-11-02', NULL, 'Fractura de muñeca', 80000),
 (3, 1, '2026-11-08', NULL, 'Hipertensión',       35000),
 (2, 2, '2026-11-10', NULL, 'Cuadro febril',      30000);
