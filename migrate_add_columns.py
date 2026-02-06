"""
Script de migración para añadir columnas faltantes a la tabla empresas.
Ejecutar con: python3 migrate_add_columns.py
"""
import pymysql
from app import create_app

app = create_app()

# Configuración de conexión directa
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '',
    'database': 'sistema_municipal',
    'charset': 'utf8mb4'
}

def run_migration():
    print("=== INICIANDO MIGRACIÓN: Añadir columnas a empresas ===\n")
    
    connection = pymysql.connect(**DB_CONFIG)
    cursor = connection.cursor()
    
    try:
        # Verificar qué columnas ya existen
        cursor.execute("DESCRIBE empresas")
        existing_columns = [row[0] for row in cursor.fetchall()]
        print(f"Columnas existentes: {', '.join(existing_columns)}\n")
        
        # Definir las nuevas columnas
        new_columns = {
            'giro': "VARCHAR(500) DEFAULT NULL COMMENT 'Descripción del giro del negocio'",
            'direccion': "VARCHAR(500) DEFAULT NULL COMMENT 'Dirección física del establecimiento'",
            'nit': "VARCHAR(50) DEFAULT NULL COMMENT 'Número de Identificación Tributaria'",
            'nrc': "VARCHAR(50) DEFAULT NULL COMMENT 'Número de Registro de Contribuyente'"
        }
        
        # Añadir solo las columnas que no existen
        for col_name, col_definition in new_columns.items():
            if col_name not in existing_columns:
                sql = f"ALTER TABLE empresas ADD COLUMN {col_name} {col_definition}"
                print(f"✓ Añadiendo columna: {col_name}")
                cursor.execute(sql)
                connection.commit()
            else:
                print(f"⊘ Columna '{col_name}' ya existe, omitiendo...")
        
        print("\n=== MIGRACIÓN COMPLETADA EXITOSAMENTE ===")
        print("\nNuevas columnas disponibles:")
        cursor.execute("DESCRIBE empresas")
        for row in cursor.fetchall():
            if row[0] in new_columns.keys():
                print(f"  - {row[0]}: {row[1]}")
        
    except Exception as e:
        connection.rollback()
        print(f"\n❌ ERROR durante la migración: {e}")
        raise
    finally:
        cursor.close()
        connection.close()

if __name__ == "__main__":
    run_migration()
