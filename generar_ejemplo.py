import pandas as pd

# Crear datos de ejemplo basados en tu imagen
data = {
    'PROPIETARIO': ['CINDY YAJAIRA ORDOÑEZ', 'CHRISTIAN RODRIGO TRUJILLO', 'SALVADOR ERNESTO CORTEZ'],
    'EMPRESA/NEGOCIO': ['TIENDA ABRAHAM', 'REPUESTOS MOTO SPORT', 'FUNERARIA JARDINES'],
    'CONTACTO': ['mpimentel_1311@hotmail.com 7885-1434', '7025-8647', '7851-5115'],
    'GIRO': ['Venta de productos básicos', 'Repuestos de moto', 'Servicios funerarios'],
    'OTRA_COLUMNA': ['', '', ''],
    'CUOTA MENSUAL': ['$ 32.00', '$ 3.00', '$ 25.45']
}

df = pd.DataFrame(data)

# Guardar como Excel
file_path = '/home/hector/Documents/sistema_empresas_municipal/ejemplo_pagos_2024.xlsx'
df.to_excel(file_path, index=False, sheet_name='PAGOS 2024')

print(f"Archivo de ejemplo creado en: {file_path}")
