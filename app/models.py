from app import db
from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(50), unique=True)
    
    # Relación para saber quién tiene este rol
    usuarios = db.relationship('Usuario', backref='role', lazy=True)

    def __repr__(self):
        return f'<Role {self.nombre}>'

class Usuario(UserMixin, db.Model):
    __tablename__ = 'usuarios'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, index=True)
    password_hash = db.Column(db.String(255))
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
        
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Rubro(db.Model):
    __tablename__ = 'rubros'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), unique=True, nullable=False)
    descripcion = db.Column(db.String(255))
    icono = db.Column(db.String(50), default='tag')
    color = db.Column(db.String(50), default='blue')
    categoria = db.Column(db.String(100)) # Opcional: para agrupar rubros

    empresas = db.relationship('Empresa', backref='rubro', lazy=True)

# --- Modelos Existentes ---


class Empresa(db.Model):
    __tablename__ = 'empresas'
    id = db.Column(db.Integer, primary_key=True)
    codigo = db.Column(db.String(100), unique=True, nullable=False)
    nombre_negocio = db.Column(db.String(255), nullable=False)
    propietario = db.Column(db.String(255))
    giro = db.Column(db.String(500))  # Descripción del negocio
    direccion = db.Column(db.String(500))  # Dirección física
    nit = db.Column(db.String(50))  # NIT
    nrc = db.Column(db.String(50))  # NRC
    distrito = db.Column(db.String(100), default="Atiquizaya")
    fecha_inscripcion = db.Column(db.Date)
    estado_actual = db.Column(db.String(255), default="ACTIVO")
    notas = db.Column(db.Text)  # Notas u observaciones generales
    rubro_id = db.Column(db.Integer, db.ForeignKey('rubros.id'), nullable=True)
    
    # Relaciones
    contactos = db.relationship('Contacto', backref='empresa', lazy=True)
    inspecciones = db.relationship('Inspeccion', backref='empresa', lazy=True)
    pagos = db.relationship('HistorialPago', backref='empresa', lazy=True)
    cerradas = db.relationship('EmpresaCerrada', backref='empresa', lazy=True)

class Contacto(db.Model):
    __tablename__ = 'contactos'
    id = db.Column(db.Integer, primary_key=True)
    empresa_id = db.Column(db.Integer, db.ForeignKey('empresas.id'))
    tipo = db.Column(db.String(20)) # 'TELEFONO' o 'EMAIL'
    valor = db.Column(db.String(150))

class HistorialPago(db.Model):
    __tablename__ = 'historial_pagos'
    id = db.Column(db.Integer, primary_key=True)
    empresa_id = db.Column(db.Integer, db.ForeignKey('empresas.id'))
    anio = db.Column(db.Integer)
    monto_mensual = db.Column(db.Numeric(10, 2))

class Inspeccion(db.Model):  # <--- Asegúrate que sea Singular
    __tablename__ = "inspecciones"
    id = db.Column(db.Integer, primary_key=True)
    empresa_id = db.Column(db.Integer, db.ForeignKey("empresas.id"), nullable=False)
    fecha = db.Column(db.DateTime, default=datetime.utcnow)
    inspector = db.Column(db.String(100))
    motivo = db.Column(db.String(255)) # Nuevo campo para SOLICITUD
    estado = db.Column(db.String(50))
    observaciones = db.Column(db.Text)

class EmpresaCerrada(db.Model): # <--- Esta también la pide routes.py
    __tablename__ = "empresas_cerradas"
    id = db.Column(db.Integer, primary_key=True)
    empresa_id = db.Column(db.Integer, db.ForeignKey("empresas.id"), nullable=False)
    razon = db.Column(db.Text)
    fecha = db.Column(db.DateTime, default=datetime.utcnow)