from app.services.sheet_classifier import classify_sheet

cols = ['ITEM', 'CODIGO DE EMPRESA', 'PROPIETARIO / REPRESENTANTE LEGAL', 'EMPRESA / NEGOCIO', 'TELEFONO / CORREO', 'INSCRIPCION', 'ESTADO', 'IMPUESTO MENSUAL  2024', 'IMPUESTO MENSUAL  2025', 'IMPUESTO MENSUAL  2026', 'Columna_10']

tipo = classify_sheet(cols)
print(f"Tipo detectado: {tipo}")
