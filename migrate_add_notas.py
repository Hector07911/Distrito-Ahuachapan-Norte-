from app import create_app, db
from sqlalchemy import text

app = create_app()

def migrate():
    with app.app_context():
        print("--- AGREGANDO COLUMNA 'notas' A LA TABLA 'empresas' ---")
        try:
            # MySQL syntax to add column
            db.session.execute(text("ALTER TABLE empresas ADD COLUMN notas TEXT AFTER estado_actual"))
            db.session.commit()
            print("✅ Columna 'notas' agregada con éxito.")
        except Exception as e:
            db.session.rollback()
            if "Duplicate column name" in str(e):
                print("⚠️ La columna 'notas' ya existe. Omitiendo.")
            else:
                print(f"❌ Error al agregar la columna: {e}")

if __name__ == "__main__":
    migrate()
