import os
from dotenv import load_dotenv
from app import create_app, db
from app.models import Empresa
from sqlalchemy import func

load_dotenv()

app = create_app()

with app.app_context():
    print("--- Diagnóstico de Estados de Empresa ---")
    
    # 1. Conteo total
    total = Empresa.query.count()
    print(f"Total empresas: {total}")

    # 2. Agrupar por estado para ver qué valores existen realmente
    estados = db.session.query(Empresa.estado_actual, func.count(Empresa.id)).group_by(Empresa.estado_actual).all()
    
    print("\nConteo por Estado Actual:")
    for estado, count in estados:
        print(f" - '{estado}': {count}")
        
    # 3. Verificar filtro exacto usado en routes.py
    activas_query = Empresa.query.filter(Empresa.estado_actual == 'ACTIVO').count()
    print(f"\nConsulta exacta (estado_actual == 'ACTIVO'): {activas_query}")
