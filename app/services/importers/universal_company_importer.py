import re
import pandas as pd
import pymysql
import sqlalchemy
from datetime import datetime
from app import db
from app.models import Empresa, Contacto, EmpresaCerrada
from app.services.importers.import_result import ImportResult

def normalize_column_name(col_name):
    if pd.isna(col_name): return ""
    # Normalizar eliminando espacios extras: "IMPUESTO  2024" -> "IMPUESTO 2024"
    return ' '.join(str(col_name).strip().upper().split())

def parse_flexible_date(val):
    if pd.isna(val) or val == "": return None
    try:
        return pd.to_datetime(val, dayfirst=True, errors='coerce').date()
    except:
        return None

def import_universal_company(df, session, sheet_name="Hoja"):
    result = ImportResult()
    # Normalizar columnas para evitar errores de espacios
    df.columns = [normalize_column_name(col) for col in df.columns]
    
    # Identificar tipo de hoja por nombre
    is_cierre = any(kw in sheet_name.upper() for kw in ["CIERRE", "CERRADA"])

            # Detectar columnas dinámicamente
    cols = df.columns.tolist()
    codigo_col = next((c for c in cols if any(k in c for k in ["CODIGO", "ITEM", "N°", "NC"])), None)
    nombre_col = next((c for c in cols if any(k in c for k in ["NEGOCIO", "EMPRESA", "VIVERO", "EXPENDIO", "ROTULO", "BANNER"])), None)
    propietario_col = next((c for c in cols if "PROPIETARIO" in c), None)
    fecha_cierre_col = next((c for c in cols if "CIERRE" in c or "FECHA" in c), None)
    
    # Nuevas columnas mapeadas
    ubicacion_col = next((c for c in cols if "UBICACION" in c or "DIRECCION" in c), None)
    inscripcion_col = next((c for c in cols if "INSCRIPCION" in c), None)

    BATCH_SIZE = 50
    rows_processed = 0

    for index, row in df.iterrows():
        try:
            # Extraer valores
            cod_val = str(row.get(codigo_col, '')).strip() if codigo_col else None
            nom_val = str(row.get(nombre_col, '')).strip().upper() if nombre_col else None
            
            # Limpieza de nulos
            if not cod_val or cod_val.lower() in ['nan', 'none', 'sin codigo']: cod_val = None
            if not nom_val or nom_val.lower() in ['nan', 'none']: nom_val = None

            # 1. Al principio del bucle, antes de buscar en la DB:
            if not nom_val or nom_val == "SIN NOMBRE" or len(nom_val) < 3:
                continue  # Ignora filas sin nombre real o muy cortos (basura del Excel)

            # Si no hay datos mínimos, saltar fila
            if not cod_val and not nom_val:
                continue

            # 1. BÚSQUEDA HÍBRIDA MEJORADA
            empresa = None
            if cod_val:
                empresa = session.query(Empresa).filter_by(codigo=cod_val).first()
            
            # Si no hay código o no se halló, buscamos por nombre exacto
            if not empresa and nom_val:
                # Buscar por nombre exacto para evitar generar duplicados
                empresa = session.query(Empresa).filter_by(nombre_negocio=nom_val).first()

            # 2. CREACIÓN CON CÓDIGO SEGURO
            if not empresa:
                # Si no hay código, usamos una marca de tiempo para que NUNCA se repita el código unique
                import time
                timestamp = int(time.time() * 1000)
                # Usamos index para garantizar unicidad en batch
                final_cod = cod_val if cod_val else f"GEN-{sheet_name[:3].upper()}-{index}-{timestamp}"
                
                empresa = Empresa(
                    codigo=final_cod[:100], # Aseguramos que no pase de los 100 de tu DB
                    nombre_negocio=nom_val[:255] if nom_val else "SIN NOMBRE",
                    estado_actual='ACTIVO' if not is_cierre else 'CERRADO'
                )
                session.add(empresa)
                session.flush() # Importante: flush para obtener ID si es nuevo
            
            # Actualizar datos básicos  
            if propietario_col and row.get(propietario_col):
                prop_val = str(row.get(propietario_col)).strip().upper()
                if prop_val and prop_val != 'NAN':
                    empresa.propietario = prop_val

            # Actualizar Ubicación (Dirección)
            if ubicacion_col and row.get(ubicacion_col):
                dir_val = str(row.get(ubicacion_col)).strip().upper()
                if dir_val and dir_val != 'NAN' and len(dir_val) > 2:
                    empresa.direccion = dir_val

            # Actualizar Fecha de Inscripción
            if inscripcion_col:
                fecha_insc = parse_flexible_date(row.get(inscripcion_col))
                if fecha_insc:
                    empresa.fecha_inscripcion = fecha_insc

            # Lógica específica de Cierres
            if is_cierre:
                empresa.estado_actual = 'CERRADO'
                fecha_f = None
                if fecha_cierre_col:
                    fecha_f = parse_flexible_date(row.get(fecha_cierre_col))
                
                # Sincronizar con tabla de historial (evitando duplicados)
                exists = session.query(EmpresaCerrada).filter_by(empresa_id=empresa.id).first()
                if not exists:
                    razon_c = str(row.get('GIRO', 'Cierre universal')).strip()
                    session.add(EmpresaCerrada(empresa_id=empresa.id, razon=razon_c, fecha=fecha_f))
            else:
                # Si viene de otra hoja, asegurar que no sobreescriba un cierre previo
                if not empresa.estado_actual:
                    empresa.estado_actual = 'ACTIVO'

            # Batch commit para estabilidad
            rows_processed += 1
            if rows_processed % BATCH_SIZE == 0:
                session.commit()
            
            result.add_ok()

        except (pymysql.err.OperationalError, sqlalchemy.exc.OperationalError) as e:
            session.rollback()
            if "2006" in str(e) or "2013" in str(e) or "Broken pipe" in str(e):
                import time
                time.sleep(2) # Pausa breve para recuperar conexión
            result.add_error(index, f"Error de conexión: {str(e)}")
            continue

        except Exception as e:
            session.rollback() # Solo revierte la fila con error
            # print(f"Error en fila {index}: {e}")
            result.add_error(index, f"Fallo en fila: {str(e)}")
            continue 

    # Commit final
    try:
        session.commit()
    except Exception as e:
        session.rollback()
        result.add_error(-1, f"Error en commit final: {str(e)}")

    return result