from app import create_app, db
from app.models import Role, Usuario
from sqlalchemy import text

app = create_app()

with app.app_context():
    print("Iniciando migración de Autenticación...")
    
    # 1. Crear tablas si no existen
    try:
        print("Creando tablas 'roles' y 'usuarios'...")
        with db.engine.connect() as conn:
            # Opción segura: SQLAlchemy create_all comprueba si existen
            db.create_all() 
        print("✅ Tablas verificadas/creadas.")
    except Exception as e:
        print(f"Error creando tablas: {e}")

    # 2. Seeding de Roles
    try:
        if not Role.query.filter_by(nombre='ADMIN').first():
            db.session.add(Role(nombre='ADMIN'))
            print(" Rol ADMIN creado.")
            
        if not Role.query.filter_by(nombre='USER').first():
            db.session.add(Role(nombre='USER'))
            print(" Rol USER creado.")
            
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        print(f"Error seeding roles: {e}")

    # 3. Seeding de Usuario Admin
    try:
        admin = Usuario.query.filter_by(username='admin').first()
        if not admin:
            admin_role = Role.query.filter_by(nombre='ADMIN').first()
            admin = Usuario(username='admin', role=admin_role)
            admin.set_password('admin2026') # CONTRASEÑA SOLICITADA
            db.session.add(admin)
            db.session.commit()
            print("✅ Usuario 'admin' creado con contraseña 'admin2026'.")
        else:
            print("ℹ️ El usuario 'admin' ya existe.")
            
    except Exception as e:
        db.session.rollback()
        print(f"Error seeding admin: {e}")

    print("Migración completada con éxito.")
