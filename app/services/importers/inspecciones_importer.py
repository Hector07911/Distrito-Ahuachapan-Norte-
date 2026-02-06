# app/services/importers/inspecciones_importer.py
from app.services.excel_classifier import normalize_header
from app.services.importers.import_result import ImportResult
from app.models import Empresa, Inspeccion
from datetime import datetime
import pandas as pd

HEADER_MAP = {
    "codigo": [
        "CODIGO DE EMPRESA",
        "CODIGO",
        "COD. EMPRESA",
        "COD EMPRESA"
    ],
    "fecha": [
        "FECHA",
        "FECHA DE INSPECCION",
        "FECHA DE ENTREGA A INSPECTORES"
    ],
    "inspector": [
        "INSPECTOR",
        "INSPECTORES"
    ],
    "resultado": [
        "RESULTADO",
        "CALIFICACION",
        "CONTROL DE CALIFICACIONES"
    ],
    "observaciones": [
        "OBSERVACIONES",
        "PROBLEMÁTICA ENCONTRADA",
        "PROBLEMATICA ENCONTRADA"
    ],
    "propietario": [
        "PROPIETARIO/A",
        "PROPIETARIO",
        "SOLICITANTE"
    ],
    "nombre_empresa": [
        "EMPRESA / NEGOCIO",
        "EMPRESA",
        "NEGOCIO"
    ],
    "solicitud": [
        "SOLICITUD"
    ]
}


def map_columns(df):
    mapped = {}
    normalized_columns = {
        normalize_header(str(col).strip()): col
        for col in df.columns
        if col and str(col).lower() != "nan"
    }
    for internal, possibles in HEADER_MAP.items():
        for p in possibles:
            p_norm = normalize_header(p)
            if p_norm in normalized_columns:
                mapped[internal] = normalized_columns[p_norm]
                break
    return mapped


def parse_fecha(valor):
    try:
        if valor is None or (isinstance(valor, float) and pd.isna(valor)):
            return None
        if pd.isna(valor):
            return None
        if isinstance(valor, datetime):
            return valor
        if isinstance(valor, pd.Timestamp):
            return valor.to_pydatetime()
        valor_str = str(valor).strip()
        if not valor_str or valor_str == "NaT":
            return None
        for fmt in ["%d/%m/%Y", "%d-%m-%Y", "%Y-%m-%d"]:
            try:
                return datetime.strptime(valor_str, fmt)
            except ValueError:
                continue
        parsed = pd.to_datetime(valor_str, errors="coerce")
        return None if pd.isna(parsed) else parsed.to_pydatetime()
    except Exception:
        return None


def safe_str(valor):
    if valor is None:
        return None
    if pd.isna(valor):
        return None
    val = str(valor).strip()
    return val if val else None


def import_inspecciones(df, session):
    result = ImportResult()
    column_map = map_columns(df)

    if not column_map:
        result.add_error(1, "No se detectaron encabezados válidos")
        return result

    print(f"[INSPECCIONES] Mapeo detectado: {column_map}")

    # OPTIMIZACIÓN: Cargar empresas existentes para evitar N+1 queries
    try:
        all_empresas = session.query(Empresa).all()
        # Normalizar llaves para comparación robusta
        empresas_by_codigo = {str(e.codigo).strip().upper(): e for e in all_empresas if e.codigo}
        empresas_by_nombre = {str(e.nombre_negocio).strip().upper(): e for e in all_empresas if e.nombre_negocio}
        
        # Crear índice de búsqueda por palabras clave para nombres parciales
        empresas_nombre_keywords = {}
        for e in all_empresas:
            if e.nombre_negocio:
                nombre_upper = str(e.nombre_negocio).upper()
                # Dividir nombre en palabras clave
                palabras = [p.strip() for p in nombre_upper.split() if len(p.strip()) > 2]
                for palabra in palabras:
                    if palabra not in empresas_nombre_keywords:
                        empresas_nombre_keywords[palabra] = []
                    empresas_nombre_keywords[palabra].append(e)
        
    except Exception as e:
        print(f"[ERROR] No se pudo precargar empresas en inspecciones: {e}")
        empresas_by_codigo = {}
        empresas_by_nombre = {}
        empresas_nombre_keywords = {}

    for index, row in df.iterrows():
        row_number = index + 2

        codigo = safe_str(row.get(column_map.get("codigo"))) if column_map.get("codigo") else None
        nombre_empresa = safe_str(row.get(column_map.get("nombre_empresa"))) if column_map.get("nombre_empresa") else None
        
        # Normalizar para búsqueda
        codigo_norm = codigo.upper() if codigo else None
        nombre_norm = nombre_empresa.upper() if nombre_empresa else None

        # Buscar empresa en cache con búsqueda mejorada
        empresa = None
        if codigo_norm:
            empresa = empresas_by_codigo.get(codigo_norm)
        if not empresa and nombre_norm:
            empresa = empresas_by_nombre.get(nombre_norm)
        
        # Búsqueda por palabras clave si no se encontró coincidencia exacta
        if not empresa and nombre_norm:
            palabras_busqueda = [p.strip() for p in nombre_norm.split() if len(p.strip()) > 2]
            for palabra in palabras_busqueda:
                if palabra in empresas_nombre_keywords:
                    # Tomar la primera coincidencia
                    empresa = empresas_nombre_keywords[palabra][0]
                    break

       # --- BLOQUE CORREGIDO: CREACIÓN DE EMPRESA SI NO EXISTE ---
        if not empresa:
            propietario = safe_str(row.get(column_map.get("propietario"))) if column_map.get("propietario") else None
            
            # Usar el código que viene en la fila, o generar uno basado en el propietario
            codigo_para_nueva = codigo if codigo else f"TEMP-{safe_str(propietario)[:10] if propietario else index}"

            if propietario or nombre_empresa:
                # Crear empresa con el CÓDIGO que antes faltaba
                empresa = Empresa(
                    codigo=codigo_para_nueva, # <--- ESTO EVITA EL ERROR DE NULL
                    nombre_negocio=nombre_empresa if nombre_empresa else propietario,
                    propietario=propietario,
                    estado_actual='ACTIVO',
                    fecha_inscripcion=datetime.now().date()
                )
                try:
                    session.add(empresa)
                    session.flush()  # Para obtener el ID
                    # Actualizar caché para no duplicar si el mismo código aparece de nuevo
                    empresas_by_codigo[str(codigo_para_nueva).strip().upper()] = empresa
                    print(f"[INSPECCIONES] Creada empresa con código: {codigo_para_nueva}")
                except Exception as e:
                    session.rollback()
                    result.add_error(row_number, f"Error creando empresa {codigo_para_nueva}: {str(e)}")
                    continue
            else:
                msg = "No se encontró empresa y no hay datos para crear una nueva"
                result.add_error(row_number, msg)
                continue
            
        empresa_id = empresa.id

        try:
            fecha = parse_fecha(row.get(column_map.get("fecha"))) if column_map.get("fecha") else None
            inspector = safe_str(row.get(column_map.get("inspector"))) if column_map.get("inspector") else None
            resultado = safe_str(row.get(column_map.get("resultado"))) if column_map.get("resultado") else None
            observaciones = safe_str(row.get(column_map.get("observaciones"))) if column_map.get("observaciones") else None
            solicitud = safe_str(row.get(column_map.get("solicitud"))) if column_map.get("solicitud") else None

            # Si no tiene fecha ni inspector ni observaciones, saltar la fila
            if not fecha and not inspector and not observaciones:
                result.add_error(row_number, "Fila sin datos útiles")
                continue

            # Combinar resultado con solicitud si existe
            # NOTA: Ahora guardamos solicitud en 'motivo', no en estado/resultado
            
            inspeccion = Inspeccion(
                empresa_id=empresa_id,
                fecha=fecha,
                inspector=inspector,
                motivo=solicitud, # <--- Nuevo campo
                estado=resultado,
                observaciones=observaciones,
            )
            session.add(inspeccion)
            result.add_ok()

        except Exception as e:
            result.add_error(row_number, str(e))

    return result