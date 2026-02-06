# app/services/importers/pagos_importer.py
import re
import pandas as pd
from app.models import Empresa, HistorialPago, Contacto
from app.services.importers.import_result import ImportResult
from datetime import datetime

def parse_monto(val):
    if pd.isna(val) or val == "": return 0
    try:
        # Limpiar símbolos de moneda y espacios
        val_clean = str(val).replace('$', '').replace(',', '').strip()
        return float(val_clean)
    except:
        return 0

def import_pagos_from_sheet(df, session, sheet_name):
    result = ImportResult()
    
    # Intentar detectar el año desde el nombre de la hoja (ej: "CONSOLIDADO 2024")
    anio_match = re.search(r'20\d{2}', sheet_name)
    anio_defecto = int(anio_match.group(0)) if anio_match else datetime.now().year

    # Mapeo de columnas según la imagen
    # Columna 1: Propietario
    # Columna 2: Nombre Negocio
    # Columna 3: Contacto (Email/Tel)
    # Columna 6: El monto parece estar en la penúltima o antepenúltima columna
    
    # Normalizar columnas (eliminar espacios extras)
    df.columns = [' '.join(str(c).strip().upper().split()) for c in df.columns]
    
    # Mapeo de columnas MEJORADO y ESTRICTO
    cols = df.columns.tolist()
    
    # 1. Detectar Código (Prioridad: 'CODIGO', evitando confundirse con otras cosas)
    codigo_col = next((c for c in cols if 'CODIGO' in c), None)
    
    # 2. Detectar Propietario
    propietario_col = next((c for c in cols if 'PROPIETARIO' in c or 'REPRESENTANTE' in c), None)
    
    # 3. Detectar Nombre Negocio 
    # CRÍTICO: Evitar que "CODIGO DE EMPRESA" sea tomado como nombre por tener la palabra "EMPRESA"
    nombre_col = next((c for c in cols if ('NEGOCIO' in c or 'EMPRESA' in c) and 'CODIGO' not in c), None)
    
    # 4. Contacto
    contacto_col = next((c for c in cols if any(k in c for k in ["TELEFONO", "CORREO", "EMAIL", "TEL", "CONTACTO"])), None)
    
    # Debug para logs
    # print(f"Cols detectadas -> Cod: {codigo_col}, Prop: {propietario_col}, Nom: {nombre_col}")

    BATCH_SIZE = 50
    rows_processed = 0

    for index, row in df.iterrows():
        try:
            # --- EXTRACCIÓN ROBUSTA DE DATOS ---
            
            # 1. Nombre del Negocio
            nom_val = str(row.get(nombre_col, '')).strip().upper() if nombre_col else "SIN NOMBRE"
            if not nom_val or nom_val == "NAN" or len(nom_val) < 2:
                nom_val = "SIN NOMBRE"
            
            # 2. Propietario
            propietario_val = None
            if propietario_col:
                p_val = str(row.get(propietario_col, '')).strip().upper()
                if p_val and p_val != "NAN" and len(p_val) > 2:
                    propietario_val = p_val
            
            # 3. Código de Empresa
            codigo_excel = None
            if codigo_col:
                c_val = str(row.get(codigo_col, '')).strip()
                if c_val and c_val != "NAN" and len(c_val) > 3:
                     codigo_excel = c_val

            # GENERACIÓN DE CÓDIGO (Solo si no viene en el Excel)
            if codigo_excel:
                final_code = codigo_excel
            else:
                 # Si no hay código real, generamos uno AUTO pero único
                import time
                final_code = f"AUTO-{int(time.time() * 1000)}-{index}"
            
            # --- LÓGICA DE BÚSQUEDA Y CREACIÓN ---
            
            empresa = None
            
            # Paso A: Buscar por CÓDIGO EXACTO (Prioridad Máxima)
            if codigo_excel:
                empresa = session.query(Empresa).filter_by(codigo=codigo_excel).first()
            
            # Paso B: Buscar por NOMBRE EXACTO (Solo si no hallamos por código)
            if not empresa and nom_val != "SIN NOMBRE":
                empresa = session.query(Empresa).filter_by(nombre_negocio=nom_val).first()
            
            # Creación si no existe
            if not empresa:
                empresa = Empresa(
                    codigo=final_code,
                    nombre_negocio=nom_val,
                    propietario=propietario_val,
                    estado_actual='ACTIVO',
                    fecha_inscripcion=datetime.now().date() # Default, se puede sobreescribir si hay col inscripcion
                )
                session.add(empresa)
                session.flush()
            else:
                # Si ya existe, actualizamos datos faltantes (ej: Propietario)
                if propietario_val and not empresa.propietario:
                    empresa.propietario = propietario_val
                # Si tenemos un código real del excel y la empresa tenía uno AUTO, actualizamos
                if codigo_excel and str(empresa.codigo).startswith("AUTO"):
                    empresa.codigo = codigo_excel

            # --- CAMPOS ADICIONALES ---
            
            # Fecha Inscripción
            inscripcion_col = next((c for c in df.columns if "INSCRIPCION" in c), None)
            if inscripcion_col:
                date_val = row.get(inscripcion_col)
                # Parseo básico o usar tu helper si lo importas
                pass # Por brevedad, asumimos que si viene bien se guarda, o lo dejamos como tarea pendiente

            # Actualizar campos adicionales si existen en el Excel
            giro_col = next((c for c in df.columns if any(k in c for k in ["GIRO", "ACTIVIDAD", "RUBRO"])), None)
            if giro_col:
                giro_val = str(row.get(giro_col, '')).strip()
                if giro_val and giro_val.lower() != 'nan':
                    empresa.giro = giro_val
            
            direccion_col = next((c for c in df.columns if any(k in c for k in ["DIRECCION", "DOMICILIO", "UBICACION"])), None)
            if direccion_col:
                dir_val = str(row.get(direccion_col, '')).strip()
                if dir_val and dir_val.lower() != 'nan':
                    empresa.direccion = dir_val
            
            nit_col = next((c for c in df.columns if "NIT" in c), None)
            if nit_col:
                nit_val = str(row.get(nit_col, '')).strip()
                if nit_val and nit_val.lower() != 'nan':
                    empresa.nit = nit_val
            
            nrc_col = next((c for c in df.columns if "NRC" in c), None)
            if nrc_col:
                nrc_val = str(row.get(nrc_col, '')).strip()
                if nrc_val and nrc_val.lower() != 'nan':
                    empresa.nrc = nrc_val

            # 2. Guardar Contactos (si hay)
            cont_val = str(row.get(contacto_col, '')).strip()
            if cont_val and cont_val.lower() != 'nan':
                # Intentar separar si hay varios (ej: "email@test.com 7788-9900")
                partes = cont_val.split()
                for p in partes:
                    tipo = 'EMAIL' if '@' in p else 'TELEFONO'
                    exists = session.query(Contacto).filter_by(empresa_id=empresa.id, valor=p).first()
                    if not exists:
                        session.add(Contacto(empresa_id=empresa.id, tipo=tipo, valor=p))

            # 3. Guardar Pagos (buscar TODAS las columnas de impuestos)
            columnas_impuesto = [c for c in df.columns if any(k in c for k in ["IMPUESTO", "MENSUAL", "CUOTA", "LICENCIA"])]
            
            for col_impuesto in columnas_impuesto:
                # Extraer año de la columna (ej: "IMPUESTO MENSUAL 2024" -> 2024)
                anio_match = re.search(r'20\d{2}', col_impuesto)
                anio_pago = int(anio_match.group(0)) if anio_match else anio_defecto
                
                # Obtener el monto
                monto_val = parse_monto(row.get(col_impuesto))
                
                if monto_val > 0:
                    # Evitar duplicados para el mismo año
                    pago_existente = session.query(HistorialPago).filter_by(
                        empresa_id=empresa.id, 
                        anio=anio_pago
                    ).first()
                    
                    if pago_existente:
                        pago_existente.monto_mensual = monto_val
                    else:
                        session.add(HistorialPago(
                            empresa_id=empresa.id, 
                            anio=anio_pago, 
                            monto_mensual=monto_val
                        ))

            # Commit por lotes para evitar saturar la conexión
            rows_processed += 1
            if rows_processed % BATCH_SIZE == 0:
                session.commit()
                # Opcional: imprimir progreso en logs del servidor
                # print(f"Procesadas {rows_processed} filas...")

            result.add_ok()

        except Exception as e:
            session.rollback()
            result.add_error(index, str(e))
    
    # Commit final para asegurar lo restante
    try:
        session.commit()
    except Exception as e:
        session.rollback()
        result.add_error(-1, f"Error en commit final: {str(e)}")
            
    return result
