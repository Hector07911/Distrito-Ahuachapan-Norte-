# app/services/excel_classifier.py

def normalize_header(text: str) -> str:
    """
    Normaliza encabezados de Excel para comparación
    """
    return (
        str(text)
        .upper()
        .strip()
        .replace("\n", " ")
        .replace("  ", " ")
    )