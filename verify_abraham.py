#!/usr/bin/env python3
from app import create_app, db
from app.models import Empresa, HistorialPago

app = create_app()
with app.app_context():
    e = db.session.query(Empresa).filter(Empresa.nombre_negocio.like('%ABRAHAM%')).first()
    if e:
        print(f'Empresa: {e.nombre_negocio} (ID: {e.id})')
        print(f'Contactos: {len(e.contactos)}')
        print(f'Pagos registrados: {len(e.pagos)}')
        for p in e.pagos:
            print(f'  - Año {p.anio}: ${p.monto_mensual}')
    else:
        print('Empresa TIENDA ABRAHAM no encontrada')
