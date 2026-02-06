from app import create_app, db
from app.models import Empresa, EmpresaCerrada, Contacto, Inspeccion, HistorialPago
from sqlalchemy import text

app = create_app()

def clean_junk():
    with app.app_context():
        print("--- INICIANDO LIMPIEZA DE DATOS BASURA ---")
        
        # Criterio: Nombre "SIN NOMBRE" y Código empieza con "AUTO-"
        # También podríamos buscar propietarios vacíos si fuera necesario
        junk_companies = Empresa.query.filter(
            Empresa.nombre_negocio == 'SIN NOMBRE',
            Empresa.codigo.like('AUTO-%')
        ).all()
        
        count = len(junk_companies)
        print(f"Se encontraron {count} registros basura.")
        
        if count == 0:
            print("No hay nada que borrar.")
            return

        print("Eliminando registros...")
        
        deleted_count = 0
        for emp in junk_companies:
            try:
                # 1. Eliminar dependencias manuales si CASCADE no está configurado o falla
                EmpresaCerrada.query.filter_by(empresa_id=emp.id).delete()
                Contacto.query.filter_by(empresa_id=emp.id).delete()
                Inspeccion.query.filter_by(empresa_id=emp.id).delete()
                HistorialPago.query.filter_by(empresa_id=emp.id).delete()
                
                # 2. Eliminar la empresa
                db.session.delete(emp)
                deleted_count += 1
            except Exception as e:
                print(f"Error borrando ID {emp.id}: {e}")

        try:
            db.session.commit()
            print(f"✅ Éxito: Se eliminaron {deleted_count} empresas basura y sus datos relacionados.")
        except Exception as e:
            db.session.rollback()
            print(f"❌ Error crítico al hacer commit: {e}")

if __name__ == "__main__":
    clean_junk()
