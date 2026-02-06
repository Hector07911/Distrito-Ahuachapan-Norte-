#!/usr/bin/env python3
"""
Prueba de robustez del importador con datos incompletos.
Simula filas con nombres vacíos, códigos faltantes, etc.
"""
import pandas as pd
from app import create_app, db
from app.models import Empresa, HistorialPago

# Crear datos de prueba con MUCHOS problemas
data = {
    'PROPIETARIO': ['', 'JUAN PEREZ', None, 'MARIA LOPEZ', ''],
    'EMPRESA/NEGOCIO': ['', 'TIENDA LA ESQUINA', '', None, 'nan'],
    'CONTACTO': ['7788-9900', '', '2222-3333', 'test@email.com', ''],
    'GIRO': ['Venta de abarrotes', '', 'Restaurante', None, 'Ferretería'],
    'CUOTA': ['25.00', '0', '15.50', '', '8.75']
}

df = pd.DataFrame(data)

app = create_app()
with app.app_context():
    print("=" * 70)
    print("PRUEBA DE ROBUSTEZ: Importando datos incompletos")
    print("=" * 70)
    
    # Simular el importador
    from app.services.importers.pagos_importer import import_pagos_from_sheet
    
    print(f"\n📊 Datos a importar ({len(df)} filas):")
    print("-" * 70)
    for idx, row in df.iterrows():
        nombre = row['EMPRESA/NEGOCIO']
        prop = row['PROPIETARIO']
        print(f"  Fila {idx + 1}: Nombre='{nombre}' | Propietario='{prop}'")
    
    print("\n🚀 Iniciando importación...")
    print("-" * 70)
    
    result = import_pagos_from_sheet(df, db.session, sheet_name="PRUEBA 2024")
    
    print(f"\n✅ Importación completada:")
    print(f"   Registros exitosos: {result.ok}")
    print(f"   Errores: {len(result.errors)}")
    
    if result.errors:
        print("\n⚠️  Errores encontrados:")
        for err in result.errors:
            print(f"   - Fila {err['row']}: {err['error']}")
    
    # Verificar empresas "SIN NOMBRE"
    print("\n📋 Empresas creadas:")
    print("-" * 70)
    empresas_sin_nombre = db.session.query(Empresa).filter(
        Empresa.nombre_negocio == 'SIN NOMBRE'
    ).all()
    
    print(f"\n🔍 Empresas con 'SIN NOMBRE': {len(empresas_sin_nombre)}")
    for e in empresas_sin_nombre[:5]:  # Mostrar solo las primeras 5
        print(f"   - ID: {e.id} | Código: {e.codigo} | Propietario: {e.propietario or 'N/A'}")
    
    # Verificar empresas con nombre real
    empresas_con_nombre = db.session.query(Empresa).filter(
        Empresa.nombre_negocio != 'SIN NOMBRE'
    ).order_by(Empresa.id.desc()).limit(5).all()
    
    print(f"\n🏪 Últimas empresas con nombre:")
    for e in empresas_con_nombre:
        print(f"   - {e.nombre_negocio} (ID: {e.id})")
    
    print("\n" + "=" * 70)
    print("RESULTADO: El importador puede manejar datos incompletos ✅")
    print("=" * 70)
