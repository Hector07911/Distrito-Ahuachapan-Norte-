from app.services.excel_reader import leer_hoja_limpia
from app.services.sheet_classifier import classify_sheet
from app.services.importers.import_manager import import_sheet
import pandas as pd
import logging
import re

logger = logging.getLogger(__name__)

def importar_excel_completo(ruta_excel, session):
    try:
        excel = pd.ExcelFile(ruta_excel)
    except Exception as e:
        print(f"[ERROR] No se pudo abrir el archivo Excel: {e}")
        return {}, {}

    resultados = {}
    hojas_admin = {}

    for hoja in excel.sheet_names:
        df = leer_hoja_limpia(excel, hoja)
        if df is None or df.empty: continue

        # 1. MANEJO DE COLUMNAS DUPLICADAS
        cols = pd.Series(df.columns)
        for d in cols[cols.duplicated()].unique():
            mask = cols == d
            cols[mask] = [f"{d}_{i}" if i != 0 else d for i in range(mask.sum())]
        df.columns = cols

        # 2. Resetear índices y Normalizar
        df = df.reset_index(drop=True)
        df.columns = [str(c).strip().upper() for c in df.columns]

        # 3. LIMPIEZA INTELIGENTE (Relajamos el filtro)
        col_codigo = next((c for c in df.columns if 'CODIGO' in c or 'ITEM' in c or 'N°' in c), None)
        col_nombre = next((c for c in df.columns if 'EMPRESA' in c or 'NEGOCIO' in c or 'PROPIETARIO' in c), None)
        
        # Filtro: Mantener fila si tiene algo en el código O algo en el nombre
        if col_codigo or col_nombre:
            # Mantener la fila si tiene algo en el código O algo en el nombre
            df = df[df[col_codigo].notna() | df[col_nombre].notna()].copy()
            # Quitamos el filtro de re.search(CAT|EM) aquí para que entren todas

        # Quitamos filas que son puras celdas vacías (basura de Excel)
        df = df.dropna(how='all')

        if df.empty:
            print(f"[{hoja}] Saltada: Realmente no hay datos")
            continue

        # 4. Clasificar
        tipo = classify_sheet(list(df.columns))
        nombre_h = hoja.upper()
        if not tipo:
            if "CIERRE" in nombre_h or "CERRADA" in nombre_h: tipo = "cierres"
            elif "INSP" in nombre_h: tipo = "inspecciones"
            else: tipo = "empresas"

        print(f"[{hoja}] Procesando como: {tipo.upper()} ({len(df)} filas)")

        # ... (código anterior igual hasta el try de procesamiento) ...

        try:
            resultado = import_sheet(tipo, df, session, sheet_name=hoja)
            
            # NO hacemos commit aquí si el import_sheet ya lo hace internamente
            # o si queremos que la transacción sea por hoja, pero sin rollback total.
            
            if resultado.ok > 0:
                print(f"[{hoja}] ✓ ÉXITO: {resultado.ok} filas guardadas")
                hojas_admin[hoja] = df.fillna("").astype(str).to_dict(orient="records")
            
            if resultado.errors:
                print(f"[{hoja}] ! ADVERTENCIA: {len(resultado.errors)} filas fallaron pero el resto se guardó.")
            
            resultados[hoja] = resultado

        except Exception as e:
            # Solo llegamos aquí si hay un error catastrófico de la hoja completa
            session.rollback()
            print(f"[ERROR] Fallo crítico en Hoja '{hoja}': {e}")
            resultados[hoja] = f"Error crítico: {str(e)}"
            
            # CRÍTICO: Si la conexión se rompió (Gone away), la sesión queda "envenenada".
            # Intentamos reiniciar la sesión para que la siguiente hoja no falle también.
            try:
                from app import db
                print(f"[RECUPERACIÓN] Intentando resetear la sesión de DB...")
                db.session.remove() 
            except Exception as ex:
                print(f"[ERROR] No se pudo resetear la sesión: {ex}")

    return resultados, hojas_admin