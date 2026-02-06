# test_db.py
from app import create_app, db
from app.models import Empresa, Contacto, HistorialPago
from datetime import datetime

app = create_app()

def test_system():
    with app.app_context():
        print("--- 🧪 INICIANDO PRUEBA DE SISTEMA ---")
        
        try:
            # 1. Limpiar base de datos de pruebas previas (Opcional)
            # db.drop_all() 
            db.create_all()
            print("✓ Tablas verificadas/creadas en MariaDB.")

            # 2. Crear una empresa de prueba (Simulando Atiquizaya)
            test_cat = "CAT-TEST-001"
            # Evitar duplicados en la prueba
            if Empresa.query.filter_by(codigo=test_cat).first():
                print("! La empresa de prueba ya existe. Saltando creación.")
            else:
                empresa = Empresa(
                    codigo=test_cat,
                    nombre_negocio="TIENDA DE PRUEBA S.A. DE C.V.",
                    propietario="JUAN PÉREZ",
                    distrito="ATIQUIZAYA"
                )
                db.session.add(empresa)
                db.session.flush() # Para obtener el ID

                # 3. Probar relación de Contactos (Lo que fallaba en el Excel)
                tel = Contacto(empresa_id=empresa.id, tipo='TELEFONO', valor='7777-1234')
                mail = Contacto(empresa_id=empresa.id, tipo='EMAIL', valor='prueba@municipio.gob.sv')
                db.session.add_all([tel, mail])

                # 4. Probar relación de Pagos
                pago = HistorialPago(empresa_id=empresa.id, anio=2025, monto_mensual=15.50)
                db.session.add(pago)

                db.session.commit()
                print("✓ Datos relacionales insertados correctamente.")

            # 5. Verificar lectura
            e = Empresa.query.filter_by(codigo=test_cat).first()

            print(f"\n🔍 RESULTADO DE BÚSQUEDA:")
            print(f"Empresa: {e.nombre_negocio}")
            print(f"Contactos registrados: {len(e.contactos)}")
            for c in e.contactos:
                print(f"  - {c.tipo}: {c.valor}")
            print(f"Pagos registrados: {len(e.pagos)} (Año {e.pagos[0].anio}: ${e.pagos[0].monto_mensual})")

            print("\n--- ✅ PRUEBA EXITOSA: El sistema está listo para el Excel ---")

        except Exception as ex:
            db.session.rollback()
            print(f"\n❌ ERROR CRÍTICO: {str(ex)}")
            print("Revisa si MariaDB está corriendo en XAMPP y si la DB existe.")

if __name__ == "__main__":
    test_system()