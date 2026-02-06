#!/usr/bin/env python3
"""
Prueba de extracción de múltiples años de impuestos.
"""
import pandas as pd
from app import create_app, db
from app.models import Empresa, HistorialPago

# Simular datos con múltiples columnas de impuestos
data = {
    'CODIGO DE EMPRESA': ['CAT-EM-001', 'CAT-EM-002'],
    'EMPRESA / NEGOCIO': ['TIENDA PRUEBA 1', 'TIENDA PRUEBA 2'],
    'PROPIETARIO': ['JUAN PEREZ', 'MARIA LOPEZ'],
    'IMPUESTO MENSUAL  2024': ['32.00', '15.50'],  # Doble espacio
    'IMPUESTO MENSUAL 2025': ['35.00', '18.00'],   # Espacio simple
    'IMPUESTO MENSUAL  2026': ['40.00', '20.00']   # Doble espacio
}

df = pd.DataFrame(data)

app = create_app()
with app.app_context():
    print("=" * 70)
    print("PRUEBA: Extracción de Múltiples Años de Impuestos")
    print("=" * 70)
    
    from app.services.importers.pagos_importer import import_pagos_from_sheet
    
    print(f"\n📊 Columnas detectadas:")
    for col in df.columns:
        print(f"   - {col}")
    
    print(f"\n🚀 Importando {len(df)} empresas...")
    result = import_pagos_from_sheet(df, db.session, sheet_name="PRUEBA 2024")
    
    print(f"\n✅ Resultado:")
    print(f"   Exitosos: {result.ok}")
    print(f"   Errores: {len(result.errors)}")
    
    # Verificar pagos guardados
    print(f"\n💰 Pagos guardados por empresa:")
    print("-" * 70)
    
    for nombre in ['TIENDA PRUEBA 1', 'TIENDA PRUEBA 2']:
        empresa = db.session.query(Empresa).filter_by(nombre_negocio=nombre).first()
        if empresa:
            print(f"\n{empresa.nombre_negocio} (ID: {empresa.id}):")
            pagos = db.session.query(HistorialPago).filter_by(empresa_id=empresa.id).order_by(HistorialPago.anio).all()
            for p in pagos:
                print(f"   - Año {p.anio}: ${p.monto_mensual}")
            
            if len(pagos) == 3:
                print("   ✅ Los 3 años se guardaron correctamente")
            else:
                print(f"   ⚠️  Solo se guardaron {len(pagos)} años (esperados: 3)")
    
    print("\n" + "=" * 70)
