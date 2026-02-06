import pandas as pd
import re
from app.models import Empresa, EmpresaCerrada, Inspeccion
from datetime import datetime
from app import db
from decimal import Decimal

def obtener_hojas_excel(ruta_excel):
    excel = pd.ExcelFile(ruta_excel)
    return excel.sheet_names

def importar_excel_una_hoja(excel, hoja):
    nombre = hoja.lower()

    if "empresa" in nombre and "cerrada" not in nombre:
        return importar_empresas(excel, hoja)
    elif "cerrada" in nombre:
        return importar_empresas_cerradas(excel, hoja)
    elif "inspeccion" in nombre:
        return importar_inspecciones(excel, hoja)
    else:
        return "Hoja ignorada"


def parse_fecha(valor):
    if pd.isna(valor):
        return None

    if isinstance(valor, datetime):
        return valor

    try:
        fecha = pd.to_datetime(valor, dayfirst=True, errors="coerce")
        if pd.isna(fecha):
            return None
        return fecha.to_pydatetime()
    except Exception:
        return None


def limpiar_telefono(valor):
    if not valor:
        return None

    valor = str(valor)

    # Buscar formatos tipo 7225-7760 o 72257760
    match = re.search(r'\b\d{4}-?\d{4}\b', valor)

    if match:
        return match.group()

    return None


def detectar_header(df):
    posibles_claves = [
        "CODIGO", "COD.", "EMPRESA", "NEGOCIO",
        "IMPUESTO", "PROPIETARIO", "RUC",
        "INSPECTOR", "FECHA"
    ]

    for i in range(min(MAX_HEADER_SCAN, len(df))):
        fila = df.iloc[i]

        # 🔥 ignora filas con muchos NaN (títulos)
        if fila.isnull().sum() > len(fila) / 2:
            continue

        fila_str = fila.astype(str).str.upper()

        hits = sum(
            fila_str.str.contains(p).any()
            for p in posibles_claves
        )

        if hits >= 2:
            return i

    return None


def importar_excel(ruta_excel):

    excel = pd.ExcelFile(ruta_excel)

    print("\nHOJAS DETECTADAS:")
    for h in excel.sheet_names:
        print(f"- [{h}]")

    resultados = {}

    for hoja in excel.sheet_names:
        nombre = hoja.lower()

        if "empresa" in nombre and "cerrada" not in nombre:
            resultados[hoja] = importar_empresas(excel, hoja)
        elif "cerrada" in nombre:
            resultados[hoja] = importar_empresas_cerradas(excel, hoja)
        elif "inspeccion" in nombre:
            resultados[hoja] = importar_inspecciones(excel, hoja)
        else:
            resultados[hoja] = "Hoja ignorada"

    return resultados

def clean_money(value):
    if not value:
        return Decimal("0.00")

    return Decimal(
        str(value)
        .replace("$", "")
        .replace(",", "")
        .strip()
    )

def import_empresas(df, session):
    column_map = map_columns(df)

    for _, row in df.iterrows():
        empresa = Empresa(
            codigo=row.get(column_map.get("codigo")),
            propietario=row.get(column_map.get("propietario")),
            nombre_negocio=row.get(column_map.get("nombre")),
            estado_actual=row.get(column_map.get("estado")),
        )

        session.add(empresa)

    session.commit()

def importar_empresas_cerradas(df):
    cerradas = 0

    for _, fila in df.iterrows():
        codigo = fila.get("codigo")
        fecha = fila.get("fecha_cierre")

        if not codigo:
            continue

        empresa = Empresa.query.filter_by(codigo=str(codigo).strip()).first()

        if empresa and empresa.estado_actual == 'ACTIVO':
            empresa.estado_actual = 'INACTIVO'

            if isinstance(fecha, pd.Timestamp):
                fecha = fecha.to_pydatetime()

            cierre = EmpresaCerrada(
                empresa_id=empresa.id,
                razon="Importado desde Excel",
                fecha=fecha
            )

            db.session.add(cierre)
            cerradas += 1

    db.session.commit()
    return f"{cerradas} empresas cerradas"

def importar_inspecciones(df):
    importadas = 0

    for _, fila in df.iterrows():
        codigo = fila.get("codigo")
        fecha = fila.get("fecha")
        inspector = fila.get("inspector")
        observaciones = fila.get("observaciones")

        if not codigo:
            continue

        empresa = Empresa.query.filter_by(codigo=str(codigo).strip()).first()

        if empresa:
            if isinstance(fecha, pd.Timestamp):
                fecha = fecha.to_pydatetime()

            inspeccion = Inspeccion(
                empresa_id=empresa.id,
                fecha=fecha,
                inspector=inspector,
                observaciones=observaciones
            )
            db.session.add(inspeccion)
            importadas += 1

    db.session.commit()
    return f"{importadas} inspecciones importadas"

def normalizar_texto(valor, max_len=None):
    if not valor:
        return None
    texto = str(valor).strip()
    texto = re.sub(r'\s+', ' ', texto)
    if max_len:
        texto = texto[:max_len]
    return texto or None


def extraer_correo(valor):
    if not valor:
        return None
    match = re.search(r'[\w\.-]+@[\w\.-]+\.\w+', str(valor))
    return match.group() if match else None


def normalizar_estado(valor):
    if not valor:
        return None

    valor = str(valor).upper()

    if "ACTIV" in valor:
        return "ACTIVA"
    if "CERR" in valor:
        return "CERRADA"
    if "SUSP" in valor:
        return "SUSPENDIDA"

    return valor[:50]


def limpiar_direccion(valor):
    return normalizar_texto(valor, 255)
