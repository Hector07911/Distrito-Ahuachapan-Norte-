import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # 1. Configuración de Seguridad
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-key-741258')

    # 2. Configuración HÍBRIDA de Base de Datos
    # Si existe DATABASE_URL (Railway/Render), se usa directamente.
    # Si no, se construye para XAMPP localmente.
    DATABASE_URL = os.getenv('DATABASE_URL')
    
    if DATABASE_URL:
        # Ajuste para Heroku/Railway si usan postgres://
        if DATABASE_URL.startswith("postgres://"):
            DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)
        SQLALCHEMY_DATABASE_URI = DATABASE_URL
    else:
        # Lógica para XAMPP local
        USER = os.getenv('MYSQL_USER', 'root')
        PASS = os.getenv('MYSQL_PASSWORD', '') 
        HOST = os.getenv('MYSQL_HOST', 'localhost')
        PORT = os.getenv('MYSQL_PORT', '3306')
        DB   = os.getenv('MYSQL_DB', 'sistema_empresas')
        XAMPP_SOCKET = '/opt/lampp/var/mysql/mysql.sock'
        
        if os.path.exists(XAMPP_SOCKET):
            SQLALCHEMY_DATABASE_URI = f'mysql+pymysql://{USER}:{PASS}@localhost/{DB}?unix_socket={XAMPP_SOCKET}&charset=utf8mb4'
        else:
            SQLALCHEMY_DATABASE_URI = f'mysql+pymysql://{USER}:{PASS}@{HOST}:{PORT}/{DB}?charset=utf8mb4'

    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = False
    
    # Opciones de Motor para estabilidad (Vital para Railway y XAMPP)
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_pre_ping": True,
        "pool_recycle": 280,
        "pool_size": 10,
        "max_overflow": 20,
    }
    
    UPLOAD_FOLDER = os.getenv('UPLOAD_FOLDER', 'uploads')
    MAX_CONTENT_LENGTH = 50 * 1024 * 1024
    ALLOWED_EXTENSIONS = {'xlsx', 'xls'}