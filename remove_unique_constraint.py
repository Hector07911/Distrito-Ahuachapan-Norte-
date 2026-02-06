"""
Script para eliminar la restricción UNIQUE de nombre_negocio.
Esto permite tener múltiples empresas con el mismo nombre (ej: "SIN NOMBRE").
"""
import pymysql

DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '',
    'database': 'sistema_municipal',
    'charset': 'utf8mb4'
}

def remove_unique_constraint():
    print("=== ELIMINANDO RESTRICCIÓN UNIQUE DE nombre_negocio ===\n")
    
    connection = pymysql.connect(**DB_CONFIG)
    cursor = connection.cursor()
    
    try:
        # Verificar si existe la restricción
        cursor.execute("""
            SELECT CONSTRAINT_NAME 
            FROM information_schema.TABLE_CONSTRAINTS 
            WHERE TABLE_SCHEMA = 'sistema_municipal' 
            AND TABLE_NAME = 'empresas' 
            AND CONSTRAINT_TYPE = 'UNIQUE'
            AND CONSTRAINT_NAME LIKE '%nombre_negocio%'
        """)
        
        constraint = cursor.fetchone()
        
        if constraint:
            constraint_name = constraint[0]
            print(f"✓ Restricción encontrada: {constraint_name}")
            
            # Eliminar la restricción
            sql = f"ALTER TABLE empresas DROP INDEX {constraint_name}"
            cursor.execute(sql)
            connection.commit()
            print(f"✅ Restricción '{constraint_name}' eliminada exitosamente")
        else:
            print("⊘ No se encontró restricción UNIQUE en nombre_negocio")
            print("   (Puede que ya haya sido eliminada)")
        
        # Verificar el estado final
        print("\n📋 Estructura actual de la tabla:")
        cursor.execute("SHOW CREATE TABLE empresas")
        create_table = cursor.fetchone()[1]
        
        if "UNIQUE" in create_table and "nombre_negocio" in create_table:
            print("⚠️  Aún existe una restricción UNIQUE")
        else:
            print("✅ No hay restricciones UNIQUE en nombre_negocio")
            print("   Ahora se pueden guardar múltiples 'SIN NOMBRE'")
        
    except Exception as e:
        connection.rollback()
        print(f"\n❌ ERROR: {e}")
        raise
    finally:
        cursor.close()
        connection.close()

if __name__ == "__main__":
    remove_unique_constraint()
