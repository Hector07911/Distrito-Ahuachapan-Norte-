# app/services/sheet_classifier.py
import re

def classify_sheet(columns, sheet_name=""):
    # Combinamos nombres de columnas y el nombre de la hoja para mayor precisión
    text_to_scan = (" ".join([str(c) for c in columns if c]) + " " + str(sheet_name)).upper()

    # 1. PRIORIDAD CRÍTICA: CIERRES e INSPECCIONES
    if re.search(r'CERRAD|CIERRE|BAJA', text_to_scan):
        return "cierres"

    if re.search(r'INSPECTOR|PROBLEMATICA|PROBLEMÁTICA|INSPECCI', text_to_scan):
        return "inspecciones"

    # 2. ESPECÍFICOS
    if "EXPENDIO" in text_to_scan:
        return "expendios"

    if "VIVERO" in text_to_scan:
        return "viveros"

    if re.search(r'ROTULO|RÓTULO|BANNER|VALLA|PUBLICI', text_to_scan):
        return "rotulos"

    # 3. MERCADOS Y MORA
    # Usamos \b para evitar que IMPUESTO coincida con PUESTO
    if re.search(r'MERCADO|\bPUESTO\b|\bPIEZA\b|\bLOCAL\b', text_to_scan):
        return "mercados"

    if re.search(r'MORA|DEUDA|MOROSIDAD|PENDIENTE', text_to_scan):
        return "mora"

    # 4. GENÉRICO: EMPRESAS
    if re.search(r'EMPRESA|NEGOCIO|CONTRIBUYENTE|CAT-EM', text_to_scan):
        return "empresas"

    return "empresas" # Default para no perder datos