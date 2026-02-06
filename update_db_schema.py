from app import create_app, db
from sqlalchemy import text

app = create_app()

with app.app_context():
    print("Iniciando actualización de esquema de base de datos...")
    
    # 1. Expandir columna estado_actual en tabla empresas
    try:
        print("Expandiendo columna 'estado_actual' en tabla 'empresas'...")
        with db.engine.connect() as conn:
            conn.execute(text("ALTER TABLE empresas MODIFY estado_actual VARCHAR(255) DEFAULT 'ACTIVO'"))
            conn.commit()
        print("✅ Columna 'estado_actual' expandida correctamente.")
    except Exception as e:
        print(f"⚠️ Nota sobre 'empresas': {e}")

    # 2. Agregar columna motivo en tabla inspecciones
    try:
        print("Agregando columna 'motivo' en tabla 'inspecciones'...")
        with db.engine.connect() as conn:
            # Primero verificamos si ya existe para no dar error
            result = conn.execute(text("SHOW COLUMNS FROM inspecciones LIKE 'motivo'"))
            if result.fetchone():
                print("ℹ️ La columna 'motivo' ya existe.")
            else:
                conn.execute(text("ALTER TABLE inspecciones ADD COLUMN motivo VARCHAR(255)"))
                conn.commit()
                print("✅ Columna 'motivo' agregada correctamente.")
    except Exception as e:
        print(f"❌ Error en 'inspecciones': {e}")

    print("Actualización completada.")
