import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # 1. Configuración de Seguridad
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-key-741258')

    # 2. Detectar entorno (development o production)
    FLASK_ENV = os.getenv('FLASK_ENV', 'production')
    
    # 3. Configuración DUAL de Base de Datos
    # DESARROLLO: usa XAMPP local
    # PRODUCCIÓN: usa DATABASE_URL de Railway
    
    if FLASK_ENV == 'development':
        # Modo desarrollo: XAMPP local
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
        
        print(f"🔧 [DESARROLLO] Conectando a XAMPP local: {DB}")
    else:
        # Modo producción: Railway
        DATABASE_URL = os.getenv('DATABASE_URL')
        
        if DATABASE_URL:
            # Railway usa mysql://, convertir a mysql+pymysql://
            if DATABASE_URL.startswith("mysql://"):
                SQLALCHEMY_DATABASE_URI = DATABASE_URL.replace("mysql://", "mysql+pymysql://", 1)
            elif DATABASE_URL.startswith("postgres://"):
                SQLALCHEMY_DATABASE_URI = DATABASE_URL.replace("postgres://", "postgresql://", 1)
            else:
                SQLALCHEMY_DATABASE_URI = DATABASE_URL
            
            print(f"🚀 [PRODUCCIÓN] Conectando a Railway")
        else:
            raise ValueError("❌ ERROR: En producción se requiere DATABASE_URL en las variables de entorno")

    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = False
    
    # Opciones de Motor optimizadas para ambos entornos
    if FLASK_ENV == 'development':
        # Desarrollo: configuración más relajada
        SQLALCHEMY_ENGINE_OPTIONS = {
            "pool_pre_ping": True,
            "pool_recycle": 3600,
            "pool_size": 5,
            "max_overflow": 10,
        }
    else:
        # Producción: configuración robusta para Railway
        SQLALCHEMY_ENGINE_OPTIONS = {
            "pool_pre_ping": True,        # Verifica conexiones antes de usar
            "pool_recycle": 280,           # Recicla conexiones cada 280s (Railway timeout ~300s)
            "pool_size": 10,               # Pool de conexiones
            "max_overflow": 20,            # Conexiones adicionales permitidas
            "connect_args": {
                "connect_timeout": 10,     # Timeout de conexión inicial
                "read_timeout": 30,        # Timeout de lectura
                "write_timeout": 30,       # Timeout de escritura
            }
        }
    
    UPLOAD_FOLDER = os.getenv('UPLOAD_FOLDER', 'uploads')
    MAX_CONTENT_LENGTH = 50 * 1024 * 1024
    ALLOWED_EXTENSIONS = {'xlsx', 'xls'}
