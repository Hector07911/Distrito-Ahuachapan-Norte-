-- Clean SQL file for Beekeeper Studio (Corrected to match app/models.py)
-- Created: 2026-02-06

-- Table structure for table `alembic_version`
CREATE TABLE IF NOT EXISTS `alembic_version` (
  `version_num` varchar(32) NOT NULL,
  PRIMARY KEY (`version_num`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

INSERT INTO `alembic_version` (`version_num`) VALUES ('ab7bdf74decc') ON DUPLICATE KEY UPDATE version_num=version_num;

-- Table structure for table `roles`
CREATE TABLE IF NOT EXISTS `roles` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `nombre` varchar(50) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `nombre` (`nombre`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

INSERT INTO `roles` (`id`, `nombre`) VALUES (1,'ADMIN'), (2,'USER') ON DUPLICATE KEY UPDATE nombre=nombre;

-- Table structure for table `empresas`
CREATE TABLE IF NOT EXISTS `empresas` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `codigo` varchar(100) NOT NULL,
  `nombre_negocio` varchar(255) NOT NULL,
  `propietario` varchar(255) DEFAULT NULL,
  `giro` varchar(500) DEFAULT NULL,
  `direccion` varchar(500) DEFAULT NULL,
  `nit` varchar(50) DEFAULT NULL,
  `nrc` varchar(50) DEFAULT NULL,
  `distrito` varchar(100) DEFAULT 'Atiquizaya',
  `fecha_inscripcion` date DEFAULT NULL,
  `estado_actual` varchar(255) DEFAULT 'ACTIVO',
  `notas` text DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `codigo` (`codigo`)
) ENGINE=InnoDB AUTO_INCREMENT=1001 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- Table structure for table `contactos`
CREATE TABLE IF NOT EXISTS `contactos` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `empresa_id` int(11) DEFAULT NULL,
  `tipo` varchar(20) DEFAULT NULL,
  `valor` varchar(150) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `empresa_id` (`empresa_id`),
  CONSTRAINT `contactos_ibfk_1` FOREIGN KEY (`empresa_id`) REFERENCES `empresas` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- Table structure for table `historial_pagos`
CREATE TABLE IF NOT EXISTS `historial_pagos` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `empresa_id` int(11) DEFAULT NULL,
  `anio` int(11) DEFAULT NULL,
  `monto_mensual` decimal(10,2) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `empresa_id` (`empresa_id`),
  CONSTRAINT `historial_pagos_ibfk_1` FOREIGN KEY (`empresa_id`) REFERENCES `empresas` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- Table structure for table `inspecciones`
CREATE TABLE IF NOT EXISTS `inspecciones` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `empresa_id` int(11) NOT NULL,
  `fecha` datetime DEFAULT NULL,
  `inspector` varchar(100) DEFAULT NULL,
  `motivo` varchar(255) DEFAULT NULL,
  `estado` varchar(50) DEFAULT NULL,
  `observaciones` text DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `empresa_id` (`empresa_id`),
  CONSTRAINT `inspecciones_ibfk_1` FOREIGN KEY (`empresa_id`) REFERENCES `empresas` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- Table structure for table `empresas_cerradas`
CREATE TABLE IF NOT EXISTS `empresas_cerradas` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `empresa_id` int(11) NOT NULL,
  `razon` text DEFAULT NULL,
  `fecha` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `empresa_id` (`empresa_id`),
  CONSTRAINT `empresas_cerradas_ibfk_1` FOREIGN KEY (`empresa_id`) REFERENCES `empresas` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- Table structure for table `usuarios`
CREATE TABLE IF NOT EXISTS `usuarios` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `username` varchar(50) DEFAULT NULL,
  `password_hash` varchar(255) DEFAULT NULL,
  `role_id` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `ix_usuarios_username` (`username`),
  KEY `role_id` (`role_id`),
  CONSTRAINT `usuarios_ibfk_1` FOREIGN KEY (`role_id`) REFERENCES `roles` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- Initial User (Optional, generic)
-- INSERT INTO `usuarios` (`username`, `password_hash`, `role_id`) VALUES ('admin', 'pbkdf2:sha256:260000$....', 1);

-- Data for `empresas` (Sample consistent with models)
-- IMPORTANT: Make sure to map 'nombre' -> 'nombre_negocio' and 'municipio' -> 'distrito'
INSERT INTO `empresas` (`id`, `codigo`, `nombre_negocio`, `distrito`, `estado_actual`) VALUES 
(1,'1','NEGOCIO PRUEBA 1','Atiquizaya','CERRADO'),
(2,'2','NOE OSMIN CHAFOYA LIBORIO','Atiquizaya','CERRADO');

-- Data for `empresas_cerradas` (Mapping razon and fecha)
INSERT INTO `empresas_cerradas` (`id`, `empresa_id`, `razon`, `fecha`) VALUES 
(1, 1, 'Cierre administrativo', '2026-02-05 20:36:46');

-- End of file
