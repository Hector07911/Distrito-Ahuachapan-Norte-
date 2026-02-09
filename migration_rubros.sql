-- SQL Script para añadir Rubros (Categorías) al sistema municipal

-- 1. Crear tabla de rubros
CREATE TABLE IF NOT EXISTS `rubros` (
  `id` INT AUTO_INCREMENT PRIMARY KEY,
  `nombre` VARCHAR(100) NOT NULL UNIQUE,
  `descripcion` VARCHAR(255),
  `icono` VARCHAR(50) DEFAULT 'tag',
  `color` VARCHAR(50) DEFAULT 'blue',
  `categoria` VARCHAR(100)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 2. Añadir columna de relación en empresas
ALTER TABLE `empresas` ADD COLUMN `rubro_id` INT DEFAULT NULL;

-- 3. Crear relación (llave foránea)
ALTER TABLE `empresas` ADD CONSTRAINT `fk_empresa_rubro` 
FOREIGN KEY (`rubro_id`) REFERENCES `rubros`(`id`) 
ON DELETE SET NULL;

-- 4. Insertar rubros iniciales recomendados
INSERT IGNORE INTO `rubros` (`nombre`, `descripcion`, `icono`, `color`, `categoria`) VALUES
('Tiendas y Abarrotes', 'Venta de productos de consumo diario', 'shopping', 'blue', 'Retail'),
('Restaurantes y Cafés', 'Servicios de alimentación y bebidas', 'food', 'orange', 'Servicios'),
('Farmacias', 'Venta de productos medicinales', 'health', 'green', 'Salud'),
('Clínicas', 'Servicios médicos y salud', 'health', 'blue', 'Salud'),
('Panaderías', 'Producción y venta de pan', 'food', 'orange', 'Alimentación'),
('Ferreterías', 'Venta de materiales de construcción', 'home', 'indigo', 'Hogar'),
('Ropa y Textil', 'Venta de prendas de vestir', 'clothes', 'rose', 'Retail');
