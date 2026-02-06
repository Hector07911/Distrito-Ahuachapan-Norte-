from app import create_app, db
from sqlalchemy import text

app = create_app()

with app.app_context():
    print("⚠️  ADVERTENCIA: ESTO BORRARÁ TODOS LOS DATOS ⚠️")
    confirm = input("Escribe 'BORRAR' para confirmar: ")
    
    if confirm == "BORRAR":
        try:
            print("Desactivando checks de llaves foráneas...")
            db.session.execute(text("SET FOREIGN_KEY_CHECKS = 0"))
            
            tables = ["inspecciones", "historial_pagos", "empresas_cerradas", "contactos", "empresas"]
            
            for table in tables:
                print(f"Vaciando tabla '{table}'...")
                db.session.execute(text(f"TRUNCATE TABLE {table}"))
                
            print("Reactivando checks...")
            db.session.execute(text("SET FOREIGN_KEY_CHECKS = 1"))
            db.session.commit()
            print("✅ Base de datos limpia. Lista para importar archivo corregido.")
            
        except Exception as e:
            db.session.rollback()
            print(f"❌ Error vaciando tablas: {e}")
    else:
        print("Operación cancelada.")
