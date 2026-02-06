from app import create_app, db
from app.models import Empresa, EmpresaCerrada, Inspeccion
from sqlalchemy import func

app = create_app()
with app.app_context():
    print("--- DIAGNÓSTICO DE DATOS ---")
    
    # 1. Conteos base
    total_empresas = db.session.query(Empresa).count()
    total_activas_en_empresa = db.session.query(Empresa).filter(Empresa.estado_actual != 'CERRADO').count()
    total_cerradas_en_empresa = db.session.query(Empresa).filter(Empresa.estado_actual == 'CERRADO').count()
    total_en_tabla_cerradas = db.session.query(EmpresaCerrada).count()
    
    print(f"Total Empresas: {total_empresas}")
    print(f"Activas (según estado): {total_activas_en_empresa}")
    print(f"Cerradas (según estado): {total_cerradas_en_empresa}")
    print(f"Registros en tabla EmpresaCerrada: {total_en_tabla_cerradas}")
    
    if total_cerradas_en_empresa != total_en_tabla_cerradas:
        print(f"ALERTA: Hay {total_cerradas_en_empresa - total_en_tabla_cerradas} empresas marcadas como CERRADO que no tienen registro en EmpresaCerrada.")
    
    # 2. Categorías
    tiendas = db.session.query(Empresa).filter(Empresa.nombre_negocio.ilike('%TIENDA%')).count()
    restaurantes = db.session.query(Empresa).filter(Empresa.nombre_negocio.ilike('%RESTAURANTE%')).count()
    
    print(f"\nConteos ILIKE (sin filtrar por activas):")
    print(f"Tiendas (ILIKE %TIENDA%): {tiendas}")
    print(f"Restaurantes (ILIKE %RESTAURANTE%): {restaurantes}")
    
    # Muestra ejemplos de nombres si son 0
    if tiendas == 0:
        print("\nEjemplos de nombres de negocios (primeros 5):")
        ejemplos = db.session.query(Empresa.nombre_negocio).limit(5).all()
        for ej in ejemplos:
            print(f"- {ej[0]}")
            
    # 3. Datos de Cerradas
    print("\nDetalle de tabla EmpresaCerrada (primeros 2):")
    cerradas = db.session.query(Empresa, EmpresaCerrada).join(EmpresaCerrada, Empresa.id == EmpresaCerrada.empresa_id).limit(2).all()
    for e, c in cerradas:
        print(f"ID: {e.id}, Código: {e.codigo}, Nombre: {e.nombre_negocio}, Razón: {c.razon}, Fecha: {c.fecha}")
