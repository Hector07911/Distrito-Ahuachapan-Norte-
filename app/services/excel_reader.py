# app/services/excel_reader.py
import pandas as pd
import logging

logger = logging.getLogger(__name__)

MAX_HEADER_SCAN = 20

def leer_excel(path):
    return pd.ExcelFile(path)

def listar_hojas(excel):
    return excel.sheet_names

def detectar_header(df):
    posibles_claves = [
        "CODIGO", "COD", "EMPRESA", "NEGOCIO",
        "IMPUESTO", "PROPIETARIO", "NIC", "NC",
        "RUC", "TELEFONO", "DIRECCION", "ESTADO",
        "DISTRITO", "INSCRIPCION", "FECHA", "ITEM"
    ]
    
    mejor_fila = None
    mejor_score = 0
    
    for i in range(min(MAX_HEADER_SCAN, len(df))):
        fila = df.iloc[i]
        
        # Contar columnas NO vacías
        columnas_validas = 0
        for val in fila:
            if pd.notna(val):
                val_str = str(val).strip().upper()
                if val_str and val_str != 'NAN' and val_str != '':
                    columnas_validas += 1
        
        # Contar keywords encontradas
        hits = 0
        for val in fila:
            if pd.notna(val):
                val_upper = str(val).upper()
                for palabra in posibles_claves:
                    if palabra in val_upper:
                        hits += 1
                        break
        
        score = (columnas_validas * 2) + (hits * 3)
        
        print(f"Fila {i}: cols={columnas_validas}, keywords={hits}, score={score}")
        print(f"  Valores: {[str(v)[:30] if pd.notna(v) else 'None' for v in fila[:5]]}")
        
        # Criterio más flexible: al menos 3 columnas O 2 keywords
        if (columnas_validas >= 3 or hits >= 2) and score > mejor_score:
            mejor_score = score
            mejor_fila = i
    
    if mejor_fila is not None:
        print(f"✓ ENCABEZADO DETECTADO EN FILA {mejor_fila} (score={mejor_score})")
    else:
        print(f"✗ NO SE DETECTÓ ENCABEZADO")
    
    return mejor_fila

def leer_hoja_limpia(excel, nombre_hoja):
    try:
        df = excel.parse(nombre_hoja, header=None)
        
        if df.empty:
            print(f"Hoja '{nombre_hoja}' vacía")
            return None
        
        print(f"\n{'='*60}")
        print(f"PROCESANDO: {nombre_hoja}")
        print(f"Dimensiones: {len(df)} filas x {len(df.columns)} columnas")
        print(f"{'='*60}")
        
        header_fila = detectar_header(df)
        
        if header_fila is None:
            print(f"ERROR: No se detectó encabezado en '{nombre_hoja}'")
            print("Primeras 5 filas:")
            for i in range(min(5, len(df))):
                print(f"  Fila {i}: {list(df.iloc[i][:5])}")
            return None
        
        header = df.iloc[header_fila]
        df.columns = header
        df = df.iloc[header_fila + 1:]
        df = df.dropna(how="all")
        
        if df.empty:
            print(f"Sin datos después del encabezado")
            return None
        
        df = df.dropna(axis=1, how='all')
        
        df.columns = [
            str(col).strip() if pd.notna(col) else f'Columna_{i}'
            for i, col in enumerate(df.columns)
        ]
        
        print(f"✓ ÉXITO: {len(df)} filas, {len(df.columns)} columnas")
        print(f"✓ Columnas: {list(df.columns)}")
        print(f"{'='*60}\n")
        
        return df
        
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
        return None