
from app.services.sheet_classifier import classify_sheet

columns = ['ITEM', 'CODIGO DE EMPRESA', 'PROPIETARIO / REPRESENTANTE LEGAL', 'EMPRESA / NEGOCIO', 'TELEFONO / CORREO', 'INSCRIPCION', 'ESTADO', 'IMPUESTO MENSUAL 2024', 'IMPUESTO MENSUAL 2025', 'IMPUESTO MENSUAL 2026', 'Columna_10']

tipo = classify_sheet(columns, "EMPRESAS-NEGOCIOS 2023 2025")
print(f"Clasificación: {tipo}")

if tipo == "empresas":
    print("✅ CORRECTO: Clasificado como empresas")
else:
    print(f"❌ ERROR: Clasificado como {tipo} (Se esperaba 'empresas')")
