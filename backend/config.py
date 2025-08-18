import os
import secrets
from datetime import timedelta
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))

class Config:
    # Basic Flask config
    SECRET_KEY = os.environ.get('SECRET_KEY') or secrets.token_hex(32)
    
    # Application info
    APP_NAME = os.environ.get('APP_NAME', 'Your Flask App')
    APP_VERSION = os.environ.get('APP_VERSION', '1.0.0')
    
    # Database config
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
    'sqlite:///' + os.path.join(basedir, "db", "app.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True,
        'pool_recycle': 300,
    }
    
    # Session security
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    PERMANENT_SESSION_LIFETIME = timedelta(hours=2)
    
    # Additional session security
    SESSION_COOKIE_NAME = os.environ.get('SESSION_COOKIE_NAME', 'session')
    SESSION_REFRESH_EACH_REQUEST = True
    
    # CSRF Protection
    WTF_CSRF_ENABLED = True
    WTF_CSRF_TIME_LIMIT = 3600
    WTF_CSRF_SECRET_KEY = os.environ.get('WTF_CSRF_SECRET_KEY') or SECRET_KEY
    
    # Rate limiting
    RATELIMIT_STORAGE_URL = os.environ.get('REDIS_URL') or 'memory://'
    RATELIMIT_DEFAULT = "100 per hour"
    RATELIMIT_ENABLED = True
    
    # Security rate limits (for the auth system)
    MAX_LOGIN_ATTEMPTS = int(os.environ.get('MAX_LOGIN_ATTEMPTS', 5))
    LOGIN_LOCKOUT_DURATION = int(os.environ.get('LOGIN_LOCKOUT_DURATION', 900))  # 15 minutes
    MAX_RESET_ATTEMPTS = int(os.environ.get('MAX_RESET_ATTEMPTS', 5))
    RESET_RATE_LIMIT_WINDOW = int(os.environ.get('RESET_RATE_LIMIT_WINDOW', 3600))  # 1 hour
    
    # Password security
    PASSWORD_MIN_LENGTH = int(os.environ.get('PASSWORD_MIN_LENGTH', 8))
    PASSWORD_MAX_LENGTH = int(os.environ.get('PASSWORD_MAX_LENGTH', 128))
    PASSWORD_REQUIRE_UPPERCASE = os.environ.get('PASSWORD_REQUIRE_UPPERCASE', 'true').lower() in ['true', 'on', '1']
    PASSWORD_REQUIRE_LOWERCASE = os.environ.get('PASSWORD_REQUIRE_LOWERCASE', 'true').lower() in ['true', 'on', '1']
    PASSWORD_REQUIRE_DIGITS = os.environ.get('PASSWORD_REQUIRE_DIGITS', 'true').lower() in ['true', 'on', '1']
    PASSWORD_REQUIRE_SPECIAL = os.environ.get('PASSWORD_REQUIRE_SPECIAL', 'true').lower() in ['true', 'on', '1']
    
    # Token security
    RESET_TOKEN_EXPIRY_HOURS = int(os.environ.get('RESET_TOKEN_EXPIRY_HOURS', 1))
    
    # Mail settings
    MAIL_SERVER = os.environ.get('MAIL_SERVER') or 'smtp.gmail.com'
    MAIL_PORT = int(os.environ.get('MAIL_PORT') or 465)
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'false').lower() in ['true', 'on', '1']
    MAIL_USE_SSL = os.environ.get('MAIL_USE_SSL', 'true').lower() in ['true', 'on', '1']
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER') or os.environ.get('MAIL_USERNAME')
    MAIL_TIMEOUT = int(os.environ.get('MAIL_TIMEOUT', 30))
    MAIL_SUPPRESS_SEND = os.environ.get('MAIL_SUPPRESS_SEND', 'false').lower() in ['true', 'on', '1']
    
    # Admin settings
    ADMIN_EMAIL = os.environ.get('ADMIN_EMAIL')
    ADMIN_USERNAME = os.environ.get('ADMIN_USERNAME', 'admin')
    
    # Frontend and security
    FRONTEND_URL = os.environ.get("FRONTEND_URL", "http://localhost:3000")
    ALLOWED_REDIRECT_DOMAINS = [
        domain.strip() 
        for domain in os.environ.get('ALLOWED_REDIRECT_DOMAINS', '').split(',') 
        if domain.strip()
    ]
    
    # CORS settings
    CORS_ORIGINS = [
        origin.strip() 
        for origin in os.environ.get('CORS_ORIGINS', FRONTEND_URL).split(',') 
        if origin.strip()
    ]
    
    # Content Security Policy
    CSP_DEFAULT_SRC = "'self'"
    CSP_SCRIPT_SRC = "'self' 'unsafe-inline'"
    CSP_STYLE_SRC = "'self' 'unsafe-inline'"
    CSP_IMG_SRC = "'self' data: https:"
    
    # File upload settings
    UPLOAD_FOLDER = os.path.join(basedir, 'app', 'static', 'uploads', 'voices')
    MAX_CONTENT_LENGTH = int(os.environ.get('MAX_CONTENT_LENGTH', 50 * 1024 * 1024))  # 50MB default
    ALLOWED_EXTENSIONS = set(ext.strip().lower() for ext in 
                           os.environ.get('ALLOWED_EXTENSIONS', 'wav,mp3,m4a,flac,ogg').split(','))
    
    # Upload security
    UPLOAD_SCAN_ENABLED = os.environ.get('UPLOAD_SCAN_ENABLED', 'false').lower() in ['true', 'on', '1']
    UPLOAD_QUARANTINE_FOLDER = os.path.join(basedir, 'quarantine')
    
    # Logging configuration
    LOG_TO_STDOUT = os.environ.get('LOG_TO_STDOUT', 'false').lower() in ['true', 'on', '1']
    LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO').upper()
    LOG_FILE = os.environ.get('LOG_FILE', os.path.join(basedir, 'logs', 'app.log'))
    LOG_MAX_BYTES = int(os.environ.get('LOG_MAX_BYTES', 10 * 1024 * 1024))  # 10MB
    LOG_BACKUP_COUNT = int(os.environ.get('LOG_BACKUP_COUNT', 5))
    
    # Security headers
    SECURITY_HEADERS = {
        'X-Content-Type-Options': 'nosniff',
        'X-Frame-Options': 'DENY',
        'X-XSS-Protection': '1; mode=block',
        'Strict-Transport-Security': 'max-age=31536000; includeSubDomains',
        'Referrer-Policy': 'strict-origin-when-cross-origin'
    }
    
    # API settings
    API_TITLE = os.environ.get('API_TITLE', 'Flask API')
    API_VERSION = os.environ.get('API_VERSION', 'v1')
    API_RATE_LIMIT = os.environ.get('API_RATE_LIMIT', '1000 per hour')
    
    # Feature flags
    ENABLE_REGISTRATION = os.environ.get('ENABLE_REGISTRATION', 'true').lower() in ['true', 'on', '1']
    ENABLE_PASSWORD_RESET = os.environ.get('ENABLE_PASSWORD_RESET', 'true').lower() in ['true', 'on', '1']
    ENABLE_EMAIL_VERIFICATION = os.environ.get('ENABLE_EMAIL_VERIFICATION', 'false').lower() in ['true', 'on', '1']
    
    # Performance settings
    SLOW_QUERY_THRESHOLD = float(os.environ.get('SLOW_QUERY_THRESHOLD', 1.0))
    
    # Monitoring
    SENTRY_DSN = os.environ.get('SENTRY_DSN')
    ENABLE_METRICS = os.environ.get('ENABLE_METRICS', 'false').lower() in ['true', 'on', '1']
    
    @staticmethod
    def init_app(app):
        """Initialize app with configuration"""
        # Create necessary directories
        os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
        os.makedirs(os.path.dirname(app.config['LOG_FILE']), exist_ok=True)
        
        if app.config.get('UPLOAD_QUARANTINE_FOLDER'):
            os.makedirs(app.config['UPLOAD_QUARANTINE_FOLDER'], exist_ok=True)


class DevelopmentConfig(Config):
    DEBUG = True
    SESSION_COOKIE_SECURE = False  # Allow HTTP in development
    
    # More verbose logging in development
    LOG_LEVEL = 'DEBUG'
    
    # Disable some security features for easier development
    WTF_CSRF_ENABLED = False  # Can be enabled if you handle CSRF in frontend
    MAIL_SUPPRESS_SEND = False 
    
    # Development-specific settings
    TEMPLATES_AUTO_RELOAD = True
    LOG_TO_STDOUT = True
    # Relaxed rate limiting for development
    RATELIMIT_DEFAULT = "1000 per hour"
    MAX_LOGIN_ATTEMPTS = 10
    
    @staticmethod
    def init_app(app):
        Config.init_app(app)
        
        # Development-specific initialization
        print(f"Running in DEVELOPMENT mode")
        print(f"Debug: {app.config['DEBUG']}")
        print(f"Database: {app.config['SQLALCHEMY_DATABASE_URI']}")


class ProductionConfig(Config):
    DEBUG = False
    
    # Enhanced database settings for production
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True,
        'pool_recycle': 300,
        'pool_size': 10,
        'max_overflow': 20,
        'pool_timeout': 30,
    }
    
    # Strict security in production
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_SAMESITE = 'Strict'  # More strict in production
    
    # Production logging
    LOG_TO_STDOUT = True  # For containerized deployments
    
    # Stricter rate limiting
    RATELIMIT_DEFAULT = "100 per hour"
    
    # Enable all security features
    WTF_CSRF_ENABLED = True
    
    # Production-specific mail settings
    MAIL_SUPPRESS_SEND = False
    
    @staticmethod
    def init_app(app):
        Config.init_app(app)
        
        # Production-specific initialization
        import logging
        from logging.handlers import RotatingFileHandler, SysLogHandler
        
        # Set up file logging if not using stdout
        if not app.config['LOG_TO_STDOUT']:
            if not os.path.exists('logs'):
                os.mkdir('logs')
            file_handler = RotatingFileHandler(
                app.config['LOG_FILE'],
                maxBytes=app.config['LOG_MAX_BYTES'],
                backupCount=app.config['LOG_BACKUP_COUNT']
            )
            file_handler.setFormatter(logging.Formatter(
                '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
            ))
            file_handler.setLevel(logging.INFO)
            app.logger.addHandler(file_handler)
        
        # Set up syslog for production if available
        if os.path.exists('/dev/log'):
            syslog_handler = SysLogHandler()
            syslog_handler.setLevel(logging.WARNING)
            app.logger.addHandler(syslog_handler)
        
        app.logger.setLevel(logging.INFO)
        app.logger.info('Application startup')


class TestingConfig(Config):
    TESTING = True
    DEBUG = True 
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False
    SESSION_COOKIE_SECURE = False
    
    # Allow emails to actually send for testing
    MAIL_SUPPRESS_SEND = False
    
    # Disable rate limiting for tests
    RATELIMIT_ENABLED = False
    
    # Logging enabled for tests
    LOG_TO_STDOUT = True
    LOG_LEVEL = 'DEBUG'
    
    # Fast testing settings
    PASSWORD_MIN_LENGTH = 4
    MAX_LOGIN_ATTEMPTS = 10
    
    # Testing-specific uploads
    UPLOAD_FOLDER = '/tmp/test_uploads'
    
    @staticmethod
    def init_app(app):
        Config.init_app(app)
        
        import logging
        # Keep logging enabled for tests
        handler = logging.StreamHandler()
        handler.setLevel(logging.DEBUG)
        handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s: %(message)s'))
        app.logger.addHandler(handler)
        app.logger.setLevel(logging.DEBUG)
        app.logger.info("Testing environment initialized")



class DockerConfig(ProductionConfig):
    """Configuration for Docker deployments"""
    
    @staticmethod
    def init_app(app):
        ProductionConfig.init_app(app)
        
        # Log to stdout for Docker
        import logging
        from logging import StreamHandler
        
        handler = StreamHandler()
        handler.setLevel(logging.INFO)
        handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s'
        ))
        app.logger.addHandler(handler)
        app.logger.setLevel(logging.INFO)


config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'docker': DockerConfig,
    'default': DevelopmentConfig
}


def get_config(config_name=None):
    """Get configuration class by name"""
    config_name = config_name or os.environ.get('FLASK_ENV', 'default')
    return config.get(config_name, DevelopmentConfig)