# Importar la clase ImportResult
from app.services.importers.import_result import ImportResult

# Importar las funciones de cada importer
from app.services.importers.empresas_importer import import_empresas
from app.services.importers.cerradas_importer import import_cerradas
from app.services.importers.inspecciones_importer import import_inspecciones
from app.services.importers.universal_company_importer import import_universal_company
from app.services.importers.pagos_importer import import_pagos_from_sheet

def import_sheet(tipo, df, session, sheet_name="Hoja"):
    if tipo == 'empresas':
        return import_pagos_from_sheet(df, session, sheet_name=sheet_name)
    elif tipo == 'cierres':
        return import_cerradas(df, session)
    elif tipo == 'inspecciones':
        return import_inspecciones(df, session)
    elif tipo in ["expendios", "mercados", "viveros", "rotulos", "piezas"]:
        # Para estos tipos usamos el importador universal
        return import_universal_company(df, session, tipo)
    else:
        result = ImportResult()
        result.add_error(0, f"No existe un importador para el tipo '{tipo}'.")
        return result
