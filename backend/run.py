#  !/usr/bin/env python3
import os
import sys
from flask.cli import FlaskGroup
from app import create_app, db
from app.models.user import User  
from app.models.score import Score  
from config import get_config

def create_application():
    """Create Flask application with proper configuration"""
    config_name = os.environ.get('FLASK_ENV', 'development')
    app = create_app(config_name)
    return app

# Create the app instance
app = create_application()

@app.shell_context_processor
def make_shell_context():
    """Make database and models available in shell context"""
    return {
        'db': db, 
        'User': User, 
        'Score': Score,
        'app': app
    }

@app.cli.command()
def init_db():
    """Initialize the database with tables"""
    with app.app_context():
        db.create_all()
        print("Database tables created successfully!")

@app.cli.command()
def drop_db():
    """Drop all database tables"""
    with app.app_context():
        if input("Are you sure you want to drop all tables? (yes/no): ").lower() == 'yes':
            db.drop_all()
            print("Database tables dropped successfully!")
        else:
            print("Operation cancelled.")

@app.cli.command()
def reset_db():
    """Reset the database (drop and recreate)"""
    with app.app_context():
        if input("Are you sure you want to reset the database? (yes/no): ").lower() == 'yes':
            db.drop_all()
            db.create_all()
            print("Database reset successfully!")
        else:
            print("Operation cancelled.")

@app.cli.command()
def create_admin():
    """Create admin user"""
    from app.auth.utils import create_user
    from werkzeug.security import generate_password_hash
    
    with app.app_context():
        admin_username = app.config.get('ADMIN_USERNAME', 'admin')
        admin_email = app.config.get('ADMIN_EMAIL', 'admin@localhost')
        
        # Check if admin already exists
        existing_admin = User.query.filter_by(username=admin_username).first()
        if existing_admin:
            print(f"Admin user '{admin_username}' already exists!")
            return
        
        # Get password from user input
        import getpass
        password = getpass.getpass("Enter admin password: ")
        confirm_password = getpass.getpass("Confirm admin password: ")
        
        if password != confirm_password:
            print("Passwords don't match!")
            return
        
        try:
            # Create admin user
            admin_user = create_user(admin_username, admin_email, password)
            
            # Set admin role if your User model supports it
            if hasattr(admin_user, 'role'):
                admin_user.role = 'admin'
                db.session.commit()
            
            print(f"Admin user '{admin_username}' created successfully!")
            
        except Exception as e:
            print(f"Error creating admin user: {str(e)}")
            db.session.rollback()

@app.cli.command()
def cleanup_tokens():
    """Clean up expired password reset tokens"""
    from app.auth.utils import cleanup_expired_tokens
    
    with app.app_context():
        count = cleanup_expired_tokens()
        print(f"Cleaned up {count} expired tokens.")

@app.cli.command()
def show_config():
    """Show current configuration (without sensitive data)"""
    sensitive_keys = [
        'SECRET_KEY', 'WTF_CSRF_SECRET_KEY', 'MAIL_PASSWORD', 
        'DATABASE_URL', 'REDIS_URL', 'SENTRY_DSN'
    ]
    
    print(f"\nCurrent Configuration ({app.config.get('FLASK_ENV', 'unknown')}):")
    print("-" * 50)
    
    for key in sorted(app.config.keys()):
        if key.startswith('_'):
            continue
            
        value = app.config[key]
        
        # Hide sensitive configuration
        if key in sensitive_keys:
            if value:
                value = f"{'*' * (len(str(value)) - 4)}{str(value)[-4:]}" if len(str(value)) > 4 else "****"
            else:
                value = "Not set"
        
        print(f"{key}: {value}")

def init_logging():
    """Initialize logging configuration"""
    import logging
    from logging.handlers import RotatingFileHandler
    
    # Don't reinitialize if already done
    if app.logger.hasHandlers():
        return
    
    # Set log level
    log_level = getattr(logging, app.config.get('LOG_LEVEL', 'INFO').upper())
    app.logger.setLevel(log_level)
    
    # Create formatters
    formatter = logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
    )
    
    # Console handler
    if app.config.get('LOG_TO_STDOUT'):
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(log_level)
        console_handler.setFormatter(formatter)
        app.logger.addHandler(console_handler)
    
    # File handler (if not in testing mode)
    if not app.config.get('TESTING'):
        log_file = app.config.get('LOG_FILE')
        if log_file:
            # Ensure log directory exists
            log_dir = os.path.dirname(log_file)
            if log_dir and not os.path.exists(log_dir):
                os.makedirs(log_dir)
            
            file_handler = RotatingFileHandler(
                log_file,
                maxBytes=app.config.get('LOG_MAX_BYTES', 10 * 1024 * 1024),
                backupCount=app.config.get('LOG_BACKUP_COUNT', 5)
            )
            file_handler.setLevel(logging.INFO)
            file_handler.setFormatter(formatter)
            app.logger.addHandler(file_handler)

def setup_error_handlers():
    """Setup global error handlers"""
    
    @app.errorhandler(404)
    def not_found_error(error):
        return {'error': 'Not found'}, 404
    
    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        app.logger.error(f'Server Error: {error}')
        return {'error': 'Internal server error'}, 500
    
    @app.errorhandler(403)
    def forbidden_error(error):
        return {'error': 'Forbidden'}, 403
    
    @app.errorhandler(429)
    def ratelimit_handler(e):
        return {'error': 'Rate limit exceeded', 'message': str(e.description)}, 429

def validate_production_config():
    """Validate configuration for production deployment"""
    if app.config.get('FLASK_ENV') != 'production':
        return
    
    required_configs = [
        'SECRET_KEY',
        'MAIL_DEFAULT_SENDER',
        'DATABASE_URL'
    ]
    
    missing_configs = []
    for config_key in required_configs:
        if not app.config.get(config_key):
            missing_configs.append(config_key)
    
    if missing_configs:
        print(f"WARNING: Missing required production configurations: {', '.join(missing_configs)}")
        if input("Continue anyway? (yes/no): ").lower() != 'yes':
            sys.exit(1)
    
    # Warn about insecure settings in production
    if app.config.get('DEBUG'):
        print("WARNING: Debug mode is enabled in production!")
    
    if not app.config.get('SESSION_COOKIE_SECURE'):
        print("WARNING: Session cookies are not secure in production!")
    
    if app.config.get('WTF_CSRF_ENABLED') is False:
        print("WARNING: CSRF protection is disabled in production!")

def run_development_server():
    """Run the development server with proper settings"""
    host = os.environ.get('FLASK_HOST', '127.0.0.1')
    port = int(os.environ.get('FLASK_PORT', 5000))
    debug = os.environ.get('FLASK_DEBUG', 'true').lower() in ['true', 'on', '1']
    
    print(f"Starting development server on http://{host}:{port}")
    print(f"Debug mode: {debug}")
    print(f"Environment: {app.config.get('FLASK_ENV', 'unknown')}")
    print("-" * 50)
    
    app.run(
        host=host,
        port=port,
        debug=debug,
        use_reloader=debug,
        use_debugger=debug,
        threaded=True
    )

if __name__ == '__main__':
    # Initialize logging
    init_logging()
    
    # Setup error handlers
    setup_error_handlers()
    
    # Validate production configuration if needed
    validate_production_config()
    
    # Create database tables if they don't exist
    with app.app_context():
        try:
            # Only create tables if they don't exist
            db.create_all()
            app.logger.info("Database tables verified/created successfully")
        except Exception as e:
            app.logger.error(f"Database initialization error: {str(e)}")
            sys.exit(1)
    
    # Check if running in production
    if app.config.get('FLASK_ENV') == 'production':
        print("Production mode detected!")
        print("Use a proper WSGI server (gunicorn, uwsgi, etc.) instead of the development server.")
        print("Example: gunicorn -w 4 -b 0.0.0.0:5000 run:app")
        
        if input("Continue with development server? (not recommended) (yes/no): ").lower() != 'yes':
            sys.exit(0)
    
    # Run the application
    run_development_server()