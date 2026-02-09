"""
Script de migración para añadir la tabla rubros y la relación en empresas.
Ejecutar con: python3 apply_rubros_migration.py
"""
import pymysql
import os
from dotenv import load_dotenv

load_dotenv()

# Intentar obtener configuración de DATABASE_URL o variables individuales
DATABASE_URL = os.getenv('DATABASE_URL')
if DATABASE_URL and DATABASE_URL.startswith("mysql://"):
    # Extraer datos de mysql://user:pass@host:port/db
    url = DATABASE_URL.replace("mysql://", "")
    user_pass, host_db = url.split("@")
    user, password = user_pass.split(":")
    host_port, db_name = host_db.split("/")
    if ":" in host_port:
        host, port = host_port.split(":")
        port = int(port)
    else:
        host = host_port
        port = 3306
else:
    host = os.getenv('MYSQL_HOST', 'localhost')
    user = os.getenv('MYSQL_USER', 'root')
    password = os.getenv('MYSQL_PASSWORD', '')
    db_name = os.getenv('MYSQL_DB', 'sistema_empresas')
    port = int(os.getenv('MYSQL_PORT', 3306))

DB_CONFIG = {
    'host': host,
    'user': user,
    'password': password,
    'database': db_name,
    'port': port,
    'charset': 'utf8mb4'
}

def run_migration():
    print(f"=== INICIANDO MIGRACIÓN en {host}/{db_name} ===\n")
    
    try:
        connection = pymysql.connect(**DB_CONFIG)
        cursor = connection.cursor()
    except Exception as e:
        print(f"❌ Error al conectar a la base de datos: {e}")
        return

    try:
        # 1. Crear tabla rubros
        print("1. Creando tabla 'rubros'...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS rubros (
                id INT AUTO_INCREMENT PRIMARY KEY,
                nombre VARCHAR(100) NOT NULL UNIQUE,
                descripcion VARCHAR(255),
                icono VARCHAR(50) DEFAULT 'tag',
                color VARCHAR(50) DEFAULT 'blue',
                categoria VARCHAR(100)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
        """)
        connection.commit()
        print("✓ Tabla 'rubros' lista.")

        # 2. Añadir columna rubro_id a empresas
        print("\n2. Añadiendo columna 'rubro_id' a 'empresas'...")
        cursor.execute("DESCRIBE empresas")
        existing_columns = [row[0] for row in cursor.fetchall()]
        
        if 'rubro_id' not in existing_columns:
            cursor.execute("ALTER TABLE empresas ADD COLUMN rubro_id INT DEFAULT NULL")
            cursor.execute("ALTER TABLE empresas ADD CONSTRAINT fk_empresa_rubro FOREIGN KEY (rubro_id) REFERENCES rubros(id)")
            connection.commit()
            print("✓ Columna 'rubro_id' y FK añadidas.")
        else:
            print("⊘ Columna 'rubro_id' ya existe.")

        # 3. Insertar rubros por defecto (opcional, para que no esté vacío)
        print("\n3. Insertando rubros por defecto...")
        rubros_default = [
            ('Tiendas y Abarrotes', 'Venta de productos de consumo diario', 'shopping', 'blue', 'Retail'),
            ('Restaurantes y Cafés', 'Servicios de alimentación y bebidas', 'food', 'orange', 'Servicios'),
            ('Farmacias', 'Venta de productos medicinales', 'health', 'green', 'Salud'),
            ('Ferreterías', 'Venta de herramientas y materiales de construcción', 'home', 'indigo', 'Hogar')
        ]
        
        for nombre, desc, icono, color, cat in rubros_default:
            cursor.execute("SELECT id FROM rubros WHERE nombre = %s", (nombre,))
            if not cursor.fetchone():
                cursor.execute("""
                    INSERT INTO rubros (nombre, descripcion, icono, color, categoria)
                    VALUES (%s, %s, %s, %s, %s)
                """, (nombre, desc, icono, color, cat))
                print(f"✓ Rubro añadido: {nombre}")
        
        connection.commit()
        
        print("\n=== MIGRACIÓN COMPLETADA EXITOSAMENTE ===")
        
    except Exception as e:
        connection.rollback()
        print(f"\n❌ ERROR durante la migración: {e}")
    finally:
        cursor.close()
        connection.close()

if __name__ == "__main__":
    run_migration()
