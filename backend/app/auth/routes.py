from flask import request, jsonify, current_app, session
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import check_password_hash, generate_password_hash
from app.auth import bp
from app.auth.utils import (
    send_password_reset_email, 
    create_user, 
    is_valid_email, 
    validate_password_strength,
    check_login_attempts,
    record_failed_login,
    record_successful_login,
    check_reset_rate_limit,
    record_reset_attempt,
    sanitize_input
)
from app.models.user import User
from app import db
from datetime import datetime, timedelta
import logging
from functools import wraps
import time

# Configure logging
logger = logging.getLogger(__name__)

# Rate limiting storage (use Redis in production)
rate_limit_storage = {}

def rate_limit(key, max_attempts=None, window_minutes=None):
    """Rate limiting using config values"""
    
    if current_app.config.get("TESTING", False):
        return True
    
    # Use config values with defaults
    if max_attempts is None:
        max_attempts = int(current_app.config.get('MAX_LOGIN_ATTEMPTS', 5))
    if window_minutes is None:
        window_minutes = int(current_app.config.get('LOGIN_LOCKOUT_DURATION', 900)) // 60

    now = time.time()
    window_start = now - (window_minutes * 60)
    
    if key not in rate_limit_storage:
        rate_limit_storage[key] = []
    
    # Clean old attempts
    rate_limit_storage[key] = [attempt for attempt in rate_limit_storage[key] if attempt > window_start]
    
    if len(rate_limit_storage[key]) >= max_attempts:
        return False
    
    rate_limit_storage[key].append(now)
    return True

def log_security_event(event_type, details, ip_address, username=None, severity="INFO"):
    """Centralized security logging"""
    log_message = f"SECURITY EVENT [{event_type}] - IP: {ip_address}"
    if username:
        log_message += f" - User: {username}"
    log_message += f" - Details: {details}"
    
    if severity == "WARNING":
        logger.warning(log_message)
    elif severity == "ERROR":
        logger.error(log_message)
    elif severity == "CRITICAL":
        logger.critical(log_message)
    else:
        logger.info(log_message)

# ----------------------
# Input Validation Decorator
# ----------------------
def validate_input(f):
    """Decorator to validate and sanitize input"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if request.is_json:
            data = request.get_json()
            if data is None:
                return jsonify({"error": "Invalid JSON"}), 400

            # Sanitize string inputs
            for key, value in data.items():
                if isinstance(value, str):
                    data[key] = sanitize_input(value)

            kwargs['data'] = data
        else:
            return jsonify({"error": "Content-Type must be application/json"}), 400

        return f(*args, **kwargs)
    return decorated_function

# ----------------------
# LOGIN
# ----------------------
@bp.route('/login', methods=['POST'])
@validate_input
def login(data):
    try:
        username = data.get('username')
        password = data.get('password')
        client_ip = request.remote_addr

        # Input validation
        if not username or not password:
            logger.warning(f"Login attempt with missing credentials from IP: {client_ip}")
            return jsonify({"login": "failed", "error": "Username and password required"}), 400

        # Rate limiting using config values
        if not rate_limit(client_ip):
            log_security_event("RATE_LIMIT_EXCEEDED", "Login attempts", client_ip, username, "WARNING")
            return jsonify({"login": "failed", "error": "Too many login attempts. Please try again later."}), 429

        # Additional validation
        if len(username) > 100 or len(password) > 200:
            return jsonify({"login": "failed", "error": "Invalid input length"}), 400

        user = User.query.filter_by(username=username).first()

        if user and check_password_hash(user.password_hash, password):
            # Check if account is locked
            can_login, error_message = check_login_attempts(user)
            if not can_login:
                return jsonify({"login": "failed", "error": error_message}), 423

            # Clear session and login user
            session.clear()
            record_successful_login(user)
            login_user(user, remember=True)

            # Set session properties
            session.permanent = True
            session.modified = True

            log_security_event("LOGIN_SUCCESS", "User logged in successfully", client_ip, username, "INFO")
            return jsonify({
                             "login": "successful", 
                             "user_id": user.id,
                             "isAdmin": "true" if (hasattr(user, 'role') and user.role == 'admin') or user.username == 'admin' else "false"
                            }), 200


        else:
            # Handle failed login attempts
            if user:
                error_message = record_failed_login(user)
                log_security_event("LOGIN_FAILED", f"Wrong password (attempt {user.failed_login_attempts})", client_ip, username, "WARNING")
            else:
                error_message = "Invalid credentials"
                log_security_event("LOGIN_FAILED", "Non-existent username", client_ip, username, "WARNING")

            return jsonify({"login": "failed", "error": error_message}), 401

    except Exception as e:
        logger.error(f"Login error: {str(e)}")
        db.session.rollback()
        return jsonify({"login": "failed", "error": "Internal server error"}), 500

# ----------------------
# REGISTER
# ----------------------
@bp.route('/register', methods=['POST'])
@validate_input
def register_api(data):
    try:
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')
        age = data.get('age')
        sex = data.get('sex')

        # Input validation
        if not all([username, email, password]):
            return jsonify({"register": "failed", "error": "Username, email, and password are required"}), 400

        # Validate input lengths
        if len(username) > 50 or len(email) > 100:
            return jsonify({"register": "failed", "error": "Username or email too long"}), 400

        # Validate email format
        if not is_valid_email(email):
            return jsonify({"register": "failed", "error": "Invalid email format"}), 400

        # Validate password strength using utils function
        is_strong, message = validate_password_strength(password)
        if not is_strong:
            return jsonify({"register": "failed", "error": message}), 400

        # Validate age if provided
        if age is not None:
            try:
                age = int(age)
                if age < 13 or age > 120:
                    return jsonify({"register": "failed", "error": "Age must be between 13 and 120"}), 400
            except (ValueError, TypeError):
                return jsonify({"register": "failed", "error": "Invalid age format"}), 400

        # Check for existing users (case-insensitive)
        existing_user = User.query.filter(
            db.or_(
                db.func.lower(User.email) == email.lower(),
                db.func.lower(User.username) == username.lower()
            )
        ).first()

        if existing_user:
            return jsonify({"register": "failed", "error": "User already exists"}), 400

        user = create_user(username, email, password, age, sex)
        logger.info(f"New user registered: {username}")
        return jsonify({"register": "successful", "user_id": user.id}), 201

    except ValueError as e:
        return jsonify({"register": "failed", "error": str(e)}), 400
    except Exception as e:
        logger.error(f"Registration error: {str(e)}")
        db.session.rollback()
        return jsonify({"register": "failed", "error": "Internal server error"}), 500

# ----------------------
# REQUEST PASSWORD RESET
# ----------------------
@bp.route('/reset-password', methods=['POST'])
@validate_input
def reset_password(data):
    try:
        email = data.get('email')
        client_ip = request.remote_addr

        if not email:
            return jsonify({"reset": "failed", "error": "Email is required"}), 400

        # Validate email format
        if not is_valid_email(email):
            return jsonify({"reset": "failed", "error": "Invalid email format"}), 400

        # Rate limiting for reset requests using config values
        max_reset_attempts = int(current_app.config.get('MAX_RESET_ATTEMPTS', 5))
        reset_window_minutes = int(current_app.config.get('RESET_RATE_LIMIT_WINDOW', 3600)) // 60
        
        if not rate_limit(f"reset_{client_ip}", max_reset_attempts, reset_window_minutes):
            logger.warning(f"Rate limit exceeded for password reset from IP: {client_ip}")
            return jsonify({"reset": "failed", "error": "Too many reset requests. Please try again later."}), 429

        user = User.query.filter(db.func.lower(User.email) == email.lower()).first()

        if user:
            # Check user-specific rate limiting
            can_reset, error_message = check_reset_rate_limit(user)
            if not can_reset:
                return jsonify({"reset": "failed", "error": error_message}), 429
            
            # Check if there's already an active reset token (not expired)
            if (user.reset_token and user.reset_token_expiry and 
                user.reset_token_expiry > datetime.utcnow()):
                return jsonify({"reset": "failed", "error": "Reset email already sent recently"}), 429
            
            record_reset_attempt(user)
            send_password_reset_email(user)
            logger.info(f"Password reset requested for email: {email}")
        else:
            logger.warning(f"Password reset requested for non-existent email: {email}")
        
        # Always return success to prevent email enumeration
        return jsonify({"reset": "successful"}), 200

    except Exception as e:
        logger.error(f"Password reset error: {str(e)}")
        return jsonify({"reset": "failed", "error": "Internal server error"}), 500

# ----------------------
# CONFIRM PASSWORD RESET
# ----------------------
@bp.route('/password-reset/<token>', methods=['POST'])
@validate_input
def api_password_reset_confirm(token, data):
    try:
        # Validate token format
        if not token or len(token) != 43:
            return jsonify({"reset": "invalidToken"}), 400

        user = User.query.filter_by(reset_token=token).first()

        if not user:
            logger.warning(f"Invalid password reset token attempted: {token[:10]}...")
            return jsonify({"reset": "invalidToken"}), 400

        # Check token expiration
        if user.reset_token_expiry and datetime.utcnow() > user.reset_token_expiry:
            user.reset_token = None
            user.reset_token_expiry = None
            db.session.commit()
            return jsonify({"reset": "expiredToken"}), 400

        new_password = data.get('newPassword')
        confirm_password = data.get('confirmNewPassword')

        if not new_password or not confirm_password:
            return jsonify({"reset": "failed", "error": "Both password fields are required"}), 400

        if new_password != confirm_password:
            return jsonify({"reset": "unmatchedPasswords"}), 400

        # Validate password strength using utils function
        is_strong, message = validate_password_strength(new_password)
        if not is_strong:
            return jsonify({"reset": "failed", "error": message}), 400

        # Update password and clear reset token
        user.password_hash = generate_password_hash(new_password)
        user.reset_token = None
        user.reset_token_expiry = None
        user.failed_login_attempts = 0
        user.locked_until = None
        
        db.session.commit()

        logger.info(f"Password reset completed for user: {user.username}")
        return jsonify({"reset": "successful"}), 200

    except Exception as e:
        logger.error(f"Password reset confirm error: {str(e)}")
        db.session.rollback()
        return jsonify({"reset": "failed", "error": "Internal server error"}), 500

# ----------------------
# LOGOUT - FIXED VERSION
# ----------------------
@bp.route('/logout', methods=['GET', 'POST'])  
@login_required
def api_logout():
    try:
        user_id = current_user.id
        username = current_user.username

        # Clear Flask-Login session
        logout_user()

        # Clear entire session
        session.clear()
        
        # Force session to be saved and marked as modified
        session.permanent = False
        session.modified = True

        logger.info(f"User logged out successfully: {username} (ID: {user_id})")
        
        # Create response with proper headers
        response = jsonify({"logoutStatus": "1", "message": "Logged out successfully"})
        
        # Clear session and remember me cookies explicitly
        response.set_cookie('session', '', expires=0, path='/', httponly=True)
        response.set_cookie('remember_token', '', expires=0, path='/', httponly=True)
        
        # Prevent caching
        response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate, max-age=0'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '0'
        
        return response, 200

    except Exception as e:
        logger.error(f"Logout error: {str(e)}")
        # Even if error occurs, try to clear session
        try:
            session.clear()
        except:
            pass
        return jsonify({"logoutStatus": "0", "error": "Logout failed"}), 500


# ----------------------
# CHECK LOGIN STATUS
# ----------------------
@bp.route('/check-login', methods=['GET'])
def check_login():
    try:
        if current_user.is_authenticated:
            response = jsonify({"logged": "true", "user_id": current_user.id})
        else:
            response = jsonify({"logged": "false"})
        
        # Always prevent caching for authentication status
        response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '0'
        
        return response
        
    except Exception as e:
        logger.error(f"Check login error: {str(e)}")
        response = jsonify({"logged": "false"})
        response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        return response


# ----------------------
# CHECK ADMIN STATUS
# ----------------------
@bp.route('/check-admin', methods=['GET'])
def check_admin():
    try:
        if current_user.is_authenticated:
            # Use role-based system instead of hardcoded username
            if hasattr(current_user, 'role') and current_user.role == 'admin':
                response = jsonify({"isAdmin": "true"})
            elif current_user.username == 'admin':  # Fallback for backward compatibility
                response = jsonify({"isAdmin": "true"})
            else:
                response = jsonify({"isAdmin": "false"})
        else:
            response = jsonify({"isAdmin": "false"})
            
        # Prevent caching
        response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        return response
        
    except Exception as e:
        logger.error(f"Check admin error: {str(e)}")
        response = jsonify({"isAdmin": "false"})
        response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        return response
    

# ----------------------
# GET CURRENT USER
# ----------------------
@bp.route('/current-user', methods=['GET'])
@login_required
def get_current_user():
    try:
        if not current_user.is_authenticated:
            return jsonify({'error': 'Unauthorized'}), 401

        response = jsonify({
            'username': current_user.username,
            'profile_photo': current_user.profile_photo if hasattr(current_user, 'profile_photo') else None
        })
        
        # Prevent caching
        response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        return response
        
    except Exception as e:
        logger.error(f"Get current user error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500


# ----------------------
# Session cleanup on app startup
# ----------------------
@bp.before_app_first_request
def cleanup_sessions():
    """Clean up any stale sessions on app startup"""
    try:
        # This would be implemented based the session storage
        # For file-based sessions, to clean up old session files
        # For Redis/database sessions, clean up expired entries
        logger.info("Session cleanup completed")
    except Exception as e:
        logger.error(f"Session cleanup error: {str(e)}")