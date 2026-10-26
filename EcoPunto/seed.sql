-- ============================================================
-- EcoPunto - Datos de prueba (seed)
-- Las contrasenas se insertan desde database.py con hash scrypt (Werkzeug 3)
-- ============================================================

INSERT INTO punto_reciclaje (nombre, direccion, localidad, latitud, longitud, horario, estado) VALUES
('EcoPunto UMB Sede Centro', 'Av. Circunvalar 60-00', 'Chapinero', 4.641230, -74.061450, 'Lunes a viernes 7:00 - 19:00', 'activo'),
('Punto Verde Parque Simon Bolivar', 'Calle 63 # 59-30', 'Teusaquillo', 4.658900, -74.093400, 'Todos los dias 6:00 - 18:00', 'activo'),
('Centro de Acopio Kennedy', 'Carrera 78K # 38-50 Sur', 'Kennedy', 4.628700, -74.155300, 'Lunes a sabado 8:00 - 17:00', 'activo'),
('EcoPunto Plaza Usaquen', 'Carrera 6 # 119-20', 'Usaquen', 4.694500, -74.030200, 'Martes a domingo 9:00 - 16:00', 'mantenimiento'),
('Punto Limpio Suba Rincon', 'Calle 131A # 91-40', 'Suba', 4.744800, -74.097600, 'Lunes a viernes 8:00 - 18:00', 'activo');

INSERT INTO tipo_residuo (nombre, categoria, unidad_medida, factor_co2, activo) VALUES
('Papel y carton', 'Aprovechable', 'kg', 1.320, 1),
('Plastico PET', 'Aprovechable', 'kg', 2.150, 1),
('Vidrio', 'Aprovechable', 'kg', 0.580, 1),
('Aluminio y metales', 'Aprovechable', 'kg', 8.900, 1),
('Residuos electronicos (RAEE)', 'Especial', 'kg', 3.400, 1),
('Aceite vegetal usado', 'Especial', 'kg', 2.700, 1);

INSERT INTO registro_residuo (id_usuario, id_punto, id_tipo, cantidad, fecha_registro, observaciones) VALUES
(2, 1, 1, 12.50, '2026-08-03 09:15:00', 'Material de oficina del semestre anterior'),
(2, 1, 2, 8.20, '2026-08-10 10:40:00', 'Botellas separadas y limpias'),
(2, 2, 3, 15.00, '2026-08-17 11:05:00', 'Frascos de vidrio de conjunto residencial'),
(3, 3, 4, 3.80, '2026-08-21 14:30:00', 'Latas de bebida compactadas'),
(3, 3, 1, 22.40, '2026-08-28 08:50:00', 'Campana escolar de recoleccion'),
(3, 5, 5, 6.10, '2026-09-04 16:20:00', 'Dos teclados y un monitor'),
(2, 5, 6, 4.50, '2026-09-09 17:00:00', 'Aceite de cocina en envase sellado'),
(3, 2, 2, 11.30, '2026-09-14 09:35:00', 'Jornada ambiental del barrio');

INSERT INTO campania (id_punto, nombre, descripcion, fecha_inicio, fecha_fin) VALUES
(1, 'Semana Ambiental UMB', 'Jornada de recoleccion de papel y RAEE en la sede Centro', '2026-09-21', '2026-09-26'),
(2, 'Reciclaton Simon Bolivar', 'Recoleccion masiva de plastico PET y vidrio', '2026-10-05', '2026-10-06'),
(3, 'Kennedy Recicla', 'Campana de sensibilizacion y acopio de metales', '2026-10-12', '2026-10-20');

INSERT INTO reporte_ambiental (id_usuario, fecha_generacion, fecha_inicio, fecha_fin, total_kg, co2_evitado) VALUES
(2, '2026-09-01 08:00:00', '2026-08-01', '2026-08-31', 35.70, 42.83),
(3, '2026-09-01 08:05:00', '2026-08-01', '2026-08-31', 26.20, 63.39);
