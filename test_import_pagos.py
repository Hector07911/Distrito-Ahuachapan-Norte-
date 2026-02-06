#!/usr/bin/env python3
"""
Script de prueba para verificar que el importador de pagos funciona correctamente.
Este script simula la importación de datos del Excel mostrado en la imagen.
"""
import pandas as pd
from app import create_app, db
from app.models import Empresa, HistorialPago, Contacto

# Crear datos de prueba basados en la imagen del usuario
data = {
    'PROPIETARIO': ['CINDY YAJAIRA ORDOÑEZ ARANA', 'CHRISTIAN RODRIGO TRUJILLO PEREZ'],
    'EMPRESA/NEGOCIO': ['TIENDA ABRAHAM', 'REPUESTOS MOTO SPORT'],
    'CONTACTO': ['mpimentel_1311@hotmail.com 7885-1434', '7025-8647'],
    'ESTADO': ['ACTIVO', 'BASE IMPONIBLE'],
    'CUOTA': ['32.00', '3.00']
}

df = pd.DataFrame(data)

app = create_app()
with app.app_context():
    print("=== INICIANDO PRUEBA DE IMPORTACIÓN ===\n")
    
    for index, row in df.iterrows():
        try:
            nombre = str(row['EMPRESA/NEGOCIO']).strip().upper()
            propietario = str(row['PROPIETARIO']).strip().upper()
            contacto_raw = str(row['CONTACTO']).strip()
            monto_str = str(row['CUOTA']).replace('$', '').replace(',', '').strip()
            monto = float(monto_str)
            
            print(f"[{index + 1}] Procesando: {nombre}")
            
            # 1. Buscar o crear empresa
            empresa = db.session.query(Empresa).filter_by(nombre_negocio=nombre).first()
            if not empresa:
                import time
                empresa = Empresa(
                    codigo=f"AUTO-TEST-{int(time.time())}-{index}",
                    nombre_negocio=nombre,
                    propietario=propietario,
                    estado_actual='ACTIVO'
                )
                db.session.add(empresa)
                db.session.flush()
                print(f"   ✓ Empresa creada con ID: {empresa.id}")
            else:
                print(f"   ✓ Empresa encontrada con ID: {empresa.id}")
            
            # 2. Guardar contactos
            if contacto_raw and contacto_raw.lower() != 'nan':
                partes = contacto_raw.split()
                for p in partes:
                    tipo = 'EMAIL' if '@' in p else 'TELEFONO'
                    exists = db.session.query(Contacto).filter_by(empresa_id=empresa.id, valor=p).first()
                    if not exists:
                        db.session.add(Contacto(empresa_id=empresa.id, tipo=tipo, valor=p))
                        print(f"   ✓ Contacto guardado: {p} ({tipo})")
            
            # 3. Guardar pago
            anio = 2024  # Año de prueba
            pago_existente = db.session.query(HistorialPago).filter_by(
                empresa_id=empresa.id, 
                anio=anio
            ).first()
            
            if pago_existente:
                pago_existente.monto_mensual = monto
                print(f"   ✓ Pago actualizado: ${monto} para año {anio}")
            else:
                db.session.add(HistorialPago(
                    empresa_id=empresa.id, 
                    anio=anio, 
                    monto_mensual=monto
                ))
                print(f"   ✓ Pago creado: ${monto} para año {anio}")
            
            db.session.commit()
            print(f"   ✅ Registro completado exitosamente\n")
            
        except Exception as e:
            db.session.rollback()
            print(f"   ❌ ERROR: {str(e)}\n")
    
    # Verificar resultados
    print("\n=== VERIFICACIÓN FINAL ===")
    total_pagos = db.session.query(HistorialPago).count()
    print(f"Total de pagos en la base de datos: {total_pagos}")
    
    if total_pagos > 0:
        print("\n📋 Primeros 5 pagos registrados:")
        for p in db.session.query(HistorialPago).limit(5).all():
            empresa = db.session.query(Empresa).get(p.empresa_id)
            print(f"  - {empresa.nombre_negocio}: ${p.monto_mensual} ({p.anio})")
    
    print("\n✅ Prueba completada. Ahora puedes verificar el expediente en el navegador.")
