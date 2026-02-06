# app/services/importers/empresas_importer.py
from app.services.excel_classifier import normalize_header
from app.models import Empresa
from app.services.importers.import_result import ImportResult
from datetime import datetime
import pandas as pd
import logging

logger = logging.getLogger(__name__)

HEADER_MAP = {
    "nombre": [
        "EMPRESA",
        "EMPRESA / NEGOCIO",
        "NEGOCIO",
        "NOMBRE EMPRESA",
        "NOMBRE"
    ],
    "distrito": [
        "DISTRITO",
        "UBICACION",
        "MUNICIPIO"
    ],
    "ruc": [
        "RUC",
        "NIC",
        "NC",
        "CODIGO",
        "CODIGO DE EMPRESA",
        "COD. EMPRESA"
    ],
    "direccion": [
        "DIRECCION",
        "DIRECCIÓN",
        "DOMICILIO"
    ],
    "telefono": [
        "TELEFONO",
        "TELÉFONO",
        "TELEFONO / CORREO",
        "CONTACTO"
    ],
    "estado": [
        "ESTADO",
        "ESTATUS"
    ],
    "fecha_registro": [
        "FECHA REGISTRO",
        "INSCRIPCION",
        "FECHA INSCRIPCION",
        "FECHA"
    ]
}


def is_empty_value(value):
    if value is None:
        return True
    if pd.isna(value):
        return True
    if isinstance(value, str) and value.strip() == "":
        return True
    return False


def safe_str(value):
    if is_empty_value(value):
        return None
    return str(value).strip()


def parse_fecha(value):
    if is_empty_value(value):
        return None
    try:
        if isinstance(value, datetime):
            return value
        if isinstance(value, pd.Timestamp):
            return value.to_pydatetime()
        value_str = str(value).strip()
        formatos = ["%d/%m/%Y", "%d-%m-%Y", "%Y-%m-%d", "%d/%m/%y", "%d-%m-%y"]
        for formato in formatos:
            try:
                return datetime.strptime(value_str, formato)
            except ValueError:
                continue
        parsed = pd.to_datetime(value_str, errors='coerce')
        return None if pd.isna(parsed) else parsed.to_pydatetime()
    except Exception as e:
        logger.warning(f"No se pudo parsear fecha '{value}': {e}")
        return None


def map_columns(df):
    mapped = {}
    normalized_columns = {}
    for col in df.columns:
        if col is None:
            continue
        col_str = str(col).strip()
        if col_str.lower() == "nan" or col_str == "":
            continue
        normalized = normalize_header(col_str)
        normalized_columns[normalized] = col

    for internal, possibles in HEADER_MAP.items():
        for p in possibles:
            p_norm = normalize_header(p)
            if p_norm in normalized_columns:
                mapped[internal] = normalized_columns[p_norm]
                break
    return mapped


def validate_empresa(row, column_map, row_number):
    errors = []
    nombre_col = column_map.get("nombre")
    if not nombre_col:
        errors.append("Columna de nombre no encontrada")
    else:
        nombre = row.get(nombre_col)
        if is_empty_value(nombre):
            errors.append("Nombre de empresa vacío")

    ruc_col = column_map.get("ruc")
    if ruc_col:
        ruc = row.get(ruc_col)
        if not is_empty_value(ruc):
            ruc_str = safe_str(ruc)
            if ruc_str and len(ruc_str) > 100:
                errors.append("RUC demasiado largo (máx 100 caracteres)")
    return errors

def import_empresas(df, session, sheet_name="Hoja"):
    result = ImportResult()
    column_map = map_columns(df)
    is_cierre = any(kw in sheet_name.upper() for kw in ["CIERRE", "CERRADA"])

    for index, row in df.iterrows():
        row_number = index + 2
        try:
            nombre = safe_str(row.get(column_map.get("nombre")))
            ruc = safe_str(row.get(column_map.get("ruc")))

            if not nombre and not ruc: continue

            # Generar código si no hay
            if not ruc:
                ruc = f"REG-{sheet_name[:3].upper()}-{index}"

            # BUSCAR SI YA EXISTE
            empresa = session.query(Empresa).filter(
                (Empresa.codigo == ruc) | (Empresa.nombre_negocio == nombre)
            ).first()

            if not empresa:
                empresa = Empresa(
                    codigo=ruc,
                    nombre_negocio=nombre,
                    estado_actual='ACTIVO' if not is_cierre else 'CERRADO'
                )
                session.add(empresa)
            else:
                # Si ya existe, solo actualizamos el estado si es una hoja de cierres
                if is_cierre:
                    empresa.estado_actual = 'CERRADO'

            # --- LA CLAVE PARA QUE NO DESAPAREZCAN ---
            session.commit() # <--- COMMIT FILA POR FILA
            result.add_ok()

        except Exception as e:
            session.rollback() # Solo revierte LA FILA que dio error
            logger.error(f"Error en fila {row_number}: {e}")
            result.add_error(row_number, str(e))
            continue # Salta a la siguiente fila sin miedo

    return result