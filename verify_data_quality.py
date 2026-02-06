from app import create_app, db
from app.models import Empresa, Inspeccion, HistorialPago, EmpresaCerrada
from sqlalchemy import text

app = create_app()

with app.app_context():
    print("=== REPORTE DE ESTADO DE BASE DE DATOS ===")
    
    # 1. Conteos Generales
    total_empresas = db.session.query(Empresa).count()
    total_inspecciones = db.session.query(Inspeccion).count()
    total_pagos = db.session.query(HistorialPago).count()
    total_cerradas = db.session.query(EmpresaCerrada).count()
    
    print(f"\n📊 RESUMEN DE REGISTROS:")
    print(f"   - Empresas:      {total_empresas}")
    print(f"   - Inspecciones:  {total_inspecciones}")
    print(f"   - Pagos:         {total_pagos}")
    print(f"   - Cerradas:      {total_cerradas}")

    # 2. Verificar Calidad de Datos (Muestra aleatoria de empresas)
    print(f"\n🧐 MUESTRA DE DATOS (Últimas 5 empresas):")
    print(f"{'ID':<5} | {'CÓDIGO':<15} | {'NOMBRE NEGOCIO':<40} | {'PROPIETARIO':<30} | {'ESTADO'}")
    print("-" * 110)
    
    empresas = db.session.query(Empresa).order_by(Empresa.id.desc()).limit(5).all()
    
    for e in empresas:
        # Cortar textos largos para tabla
        nom = (e.nombre_negocio[:37] + '...') if e.nombre_negocio and len(e.nombre_negocio) > 37 else (e.nombre_negocio or "NULL")
        prop = (e.propietario[:27] + '...') if e.propietario and len(e.propietario) > 27 else (e.propietario or "NULL")
        cod = e.codigo or "NULL"
        est = (e.estado_actual[:15] + '...') if e.estado_actual and len(e.estado_actual) > 15 else (e.estado_actual or "NULL")
        
        print(f"{e.id:<5} | {cod:<15} | {nom:<40} | {prop:<30} | {est}")

    # 3. Verificar Inspecciones con 'Motivo'
    print(f"\n🔎 MUESTRA DE INSPECCIONES (Verificando campo 'Motivo'):")
    inspecciones = db.session.query(Inspeccion).limit(3).all()
    if inspecciones:
        for i in inspecciones:
            motivo = i.motivo or "NULL"
            estado = i.estado or "NULL"
            print(f"   - Insp #{i.id}: Motivo='{motivo}', Resultado='{estado}'")
    else:
        print("   (No hay inspecciones registradas)")

    print("\n============================================")
