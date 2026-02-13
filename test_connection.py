#!/usr/bin/env python3
"""
Script de diagnóstico de conexión a base de datos
Muestra el entorno activo y prueba la conexión
"""
import os
import sys
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

def test_connection():
    print("=" * 60)
    print("🔍 DIAGNÓSTICO DE CONEXIÓN A BASE DE DATOS")
    print("=" * 60)
    
    # Mostrar entorno
    flask_env = os.getenv('FLASK_ENV', 'production')
    print(f"\n📍 Entorno actual: {flask_env.upper()}")
    
    if flask_env == 'development':
        print("   → Usando XAMPP local para desarrollo")
        print(f"   → Base de datos: {os.getenv('MYSQL_DB', 'sistema_empresas')}")
        print(f"   → Host: {os.getenv('MYSQL_HOST', 'localhost')}")
        print(f"   → Puerto: {os.getenv('MYSQL_PORT', '3306')}")
    else:
        print("   → Usando Railway para producción")
        db_url = os.getenv('DATABASE_URL', 'NO CONFIGURADO')
        if db_url != 'NO CONFIGURADO':
            # Ocultar password en la salida
            safe_url = db_url.split('@')[1] if '@' in db_url else db_url
            print(f"   → Servidor: {safe_url}")
        else:
            print("   ⚠️  DATABASE_URL no está configurado!")
    
    print("\n" + "-" * 60)
    print("🔌 Intentando conectar a la base de datos...")
    print("-" * 60)
    
    try:
        # Importar después de mostrar la configuración
        from app import create_app, db
        from app.models import Empresa
        
        app = create_app()
        
        with app.app_context():
            # Intentar una consulta simple
            count = Empresa.query.count()
            
            print("\n✅ ¡CONEXIÓN EXITOSA!")
            print(f"   → Total de empresas en la base de datos: {count}")
            
            # Mostrar información adicional
            print("\n📊 Información de la conexión:")
            print(f"   → URI: {app.config['SQLALCHEMY_DATABASE_URI'].split('@')[1] if '@' in app.config['SQLALCHEMY_DATABASE_URI'] else 'local'}")
            print(f"   → Pool size: {app.config['SQLALCHEMY_ENGINE_OPTIONS'].get('pool_size', 'N/A')}")
            print(f"   → Pool recycle: {app.config['SQLALCHEMY_ENGINE_OPTIONS'].get('pool_recycle', 'N/A')}s")
            
            return True
            
    except Exception as e:
        print("\n❌ ERROR DE CONEXIÓN")
        print(f"   → Tipo: {type(e).__name__}")
        print(f"   → Mensaje: {str(e)}")
        
        if flask_env == 'development':
            print("\n💡 Sugerencias para desarrollo local:")
            print("   1. Verifica que XAMPP esté corriendo")
            print("   2. Asegúrate de que MySQL esté iniciado")
            print("   3. Verifica que la base de datos 'sistema_empresas' exista")
            print("   4. Comando para crear DB: mysql -u root -e 'CREATE DATABASE sistema_empresas;'")
        else:
            print("\n💡 Sugerencias para producción:")
            print("   1. Verifica que DATABASE_URL esté configurado en Railway")
            print("   2. Asegúrate de que el servicio MySQL esté activo en Railway")
            print("   3. Revisa los logs de Railway para más detalles")
        
        return False
    
    finally:
        print("\n" + "=" * 60)

if __name__ == "__main__":
    success = test_connection()
    sys.exit(0 if success else 1)
