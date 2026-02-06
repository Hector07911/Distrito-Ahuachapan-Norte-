# app/services/importers/cerradas_importer.py
from app.services.excel_classifier import normalize_header
from app.services.importers.import_result import ImportResult
from app.models import Empresa, EmpresaCerrada
from datetime import datetime
import pandas as pd

HEADER_MAP = {
    "codigo": [
        "CODIGO DE EMPRESA",
        "CODIGO",
        "COD. EMPRESA",
        "N°",
        "ITEM",
        "NC"
    ],
    "nombre": [
        "EMPRESA / NEGOCIO",
        "EMPRESA",
        "NEGOCIO",
        "EMPRESA/NEGOCIO",
        "NOMBRE"
    ],
    "razon": [
        "MOTIVO DE CIERRE",
        "RAZON DE CIERRE",
        "GIRO",
        "MOTIVO"
    ],
    "fecha_cierre": [
        "FECHA DE CIERRE",
        "FECHA CIERRE",
        "FECHA"
    ],
    "estado": [
        "ESTADO"
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
        if not valor_str or valor_str == "NaT" or valor_str.lower() == "none":
            return None
        for fmt in ["%d/%m/%Y", "%d-%m-%Y", "%Y-%m-%d"]:
            try:
                return datetime.strptime(valor_str, fmt)
            except ValueError:
                continue
        parsed = pd.to_datetime(valor_str, dayfirst=True, errors="coerce")
        return None if pd.isna(parsed) else parsed.to_pydatetime()
    except Exception:
        return None


def import_cerradas(df, session):
    result = ImportResult()
    column_map = map_columns(df)

    if not column_map:
        result.add_error(1, "No se detectaron encabezados válidos")
        return result

    print(f"[CERRADAS] Mapeo detectado: {column_map}")

    # OPTIMIZACIÓN: Cargar empresas existentes para evitar N+1 queries
    try:
        all_empresas = session.query(Empresa).all()
        # Cache con llaves normalizadas (Mayúsculas y sin espacios)
        empresas_by_codigo = {str(e.codigo).strip().upper(): e for e in all_empresas if e.codigo}
        empresas_by_nombre = {str(e.nombre_negocio).strip().upper(): e for e in all_empresas if e.nombre_negocio}
    except Exception as e:
        print(f"[ERROR] No se pudo precargar empresas: {e}")
        empresas_by_codigo = {}
        empresas_by_nombre = {}

    BATCH_SIZE = 50
    rows_processed = 0

    for index, row in df.iterrows():
        row_number = index + 2

        codigo = row.get(column_map.get("codigo")) if column_map.get("codigo") else None
        nombre = row.get(column_map.get("nombre")) if column_map.get("nombre") else None

        # Limpiar y normalizar valores del Excel
        codigo_norm = str(codigo).strip().upper() if codigo and not pd.isna(codigo) else None
        nombre_norm = str(nombre).strip().upper() if nombre and not pd.isna(nombre) else None

        # Buscar empresa en el cache usando llaves normalizadas
        empresa = None
        if codigo_norm:
            empresa = empresas_by_codigo.get(codigo_norm)
        if not empresa and nombre_norm:
            empresa = empresas_by_nombre.get(nombre_norm)

        if not empresa:
            msg = f"Empresa no encontrada"
            if codigo:
                msg += f" (codigo: {codigo})"
            elif nombre:
                msg += f" (nombre: {nombre})"
            result.add_error(row_number, msg)
            continue

        try:
            # Actualizar estado a CERRADO (consistente con el resto del app)
            empresa.estado_actual = 'CERRADO'

            fecha_cierre = parse_fecha(row.get(column_map.get("fecha_cierre"))) if column_map.get("fecha_cierre") else None
            razon = row.get(column_map.get("razon")) if column_map.get("razon") else None
            razon = str(razon).strip() if razon and not pd.isna(razon) else "Cierre importado"

            # EVITAR DUPLICADOS: Si ya existe un registro en historia para esta empresa y fecha
            if fecha_cierre:
                exists = session.query(EmpresaCerrada).filter_by(
                    empresa_id=empresa.id,
                    fecha=fecha_cierre
                ).first()
            else:
                exists = session.query(EmpresaCerrada).filter_by(
                    empresa_id=empresa.id
                ).first()

            if not exists:
                cerrada = EmpresaCerrada(
                    empresa_id=empresa.id,
                    razon=razon,
                    fecha=fecha_cierre
                )
                session.add(cerrada)
            
            # Batch commit
            rows_processed += 1
            if rows_processed % BATCH_SIZE == 0:
                session.commit()

            result.add_ok()

        except Exception as e:
            session.rollback()
            result.add_error(row_number, str(e))

    # Commit final
    try:
        session.commit()
    except Exception as e:
        session.rollback()
        result.add_error(-1, f"Error en commit final: {str(e)}")

    return result