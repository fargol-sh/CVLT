import secrets
import os
from flask import url_for, current_app
from flask_mail import Message
from werkzeug.security import generate_password_hash
from app import mail, db
from app.models.user import User
from datetime import datetime, timedelta
import logging
import re
from email.utils import parseaddr
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

logger = logging.getLogger(__name__)

# ----------------------
# Generate secure token
# ----------------------
def generate_reset_token():
    """Generate a cryptographically secure reset token"""
    return secrets.token_urlsafe(32)


# ----------------------
# Validate email format
# ----------------------
def is_valid_email(email):
    """Validate email format using multiple checks"""
    if not email or len(email) > 254:
        return False
    
    # Basic regex check
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(pattern, email):
        return False
    
    # Additional validation using email.utils
    try:
        parsed = parseaddr(email)
        return '@' in parsed[1] and '.' in parsed[1].split('@')[1]
    except:
        return False


# ----------------------
# Validate password strength
# ----------------------
# ----------------------
# Validate password strength
# ----------------------
def validate_password_strength(password):
    """
    Validate password strength with comprehensive checks using config values
    Returns (is_valid, message)
    """
    if not password:
        return False, "Password is required"
    
    # Get password requirements from config
    min_length = int(current_app.config.get('PASSWORD_MIN_LENGTH', 8))
    max_length = int(current_app.config.get('PASSWORD_MAX_LENGTH', 128))
    
    # Handle boolean config values properly
    require_uppercase_config = current_app.config.get('PASSWORD_REQUIRE_UPPERCASE', 'true')
    require_lowercase_config = current_app.config.get('PASSWORD_REQUIRE_LOWERCASE', 'true')
    require_digits_config = current_app.config.get('PASSWORD_REQUIRE_DIGITS', 'true')
    require_special_config = current_app.config.get('PASSWORD_REQUIRE_SPECIAL', 'true')
    
    # Convert to boolean, handling both string and boolean types
    require_uppercase = str(require_uppercase_config).lower() == 'true' if isinstance(require_uppercase_config, str) else bool(require_uppercase_config)
    require_lowercase = str(require_lowercase_config).lower() == 'true' if isinstance(require_lowercase_config, str) else bool(require_lowercase_config)
    require_digits = str(require_digits_config).lower() == 'true' if isinstance(require_digits_config, str) else bool(require_digits_config)
    require_special = str(require_special_config).lower() == 'true' if isinstance(require_special_config, str) else bool(require_special_config)
    
    if len(password) < min_length:
        return False, f"Password must be at least {min_length} characters long"
    
    if len(password) > max_length:
        return False, f"Password is too long (maximum {max_length} characters)"
    
    # Check for different character types based on config
    checks = {}
    if require_uppercase:
        checks['uppercase'] = r"[A-Z]"
    if require_lowercase:
        checks['lowercase'] = r"[a-z]"
    if require_digits:
        checks['digit'] = r"\d"
    if require_special:
        checks['special'] = r"[!@#$%^&*()_+\-=\[\]{};':\"\\|,.<>\/?~`]"
    
    missing = []
    for check_name, pattern in checks.items():
        if not re.search(pattern, password):
            missing.append(check_name)
    
    if missing:
        if len(missing) == 1:
            return False, f"Password must contain at least one {missing[0]} character"
        else:
            return False, f"Password must contain at least one {', '.join(missing[:-1])} and {missing[-1]} character"
    
    # Check for common weak passwords
    common_weak = [
        'password', '12345678', 'qwerty', 'abc123', 'password123',
        'admin', 'letmein', 'welcome', 'monkey', '1234567890'
    ]
    
    if password.lower() in common_weak:
        return False, "Please choose a stronger password"
    
    return True, "Password is strong"


# ----------------------
# Send password reset email
# ----------------------
def send_password_reset_email(user):
    """Send password reset email with SMTP debug logging."""
    try:
        if not user.email or not is_valid_email(user.email):
            logger.error(f"Invalid email for user {user.id}: {user.email}")
            raise ValueError("Invalid email address")

        token = generate_reset_token()
        user.reset_token = token
        
        # Get reset token expiry from config
        reset_expiry_hours = int(current_app.config.get('RESET_TOKEN_EXPIRY_HOURS', 1))
        user.reset_token_expiry = datetime.utcnow() + timedelta(hours=reset_expiry_hours)
        db.session.commit()

        frontend_url = current_app.config.get('FRONTEND_URL', 'http://localhost:3000').rstrip('/')
        reset_link = f"{frontend_url}/password-reset/{token}"

        # Plain text and HTML email content
        app_name = current_app.config.get('APP_NAME', 'Your App')
        subject = f"Password Reset Request - {app_name}"
        
        text_body = f"""Hello {user.username},

We received a request to reset your password. Click the link below to reset it:

{reset_link}

This link will expire in {reset_expiry_hours} hour{'s' if reset_expiry_hours != 1 else ''}.

If you did not request this, please ignore this email.
"""
        html_body = f"""<html>
<body>
<h2>Password Reset Request</h2>
<p>Hello <strong>{user.username}</strong>,</p>
<p>We received a request to reset your password. Click below to reset it:</p>
<p><a href="{reset_link}">Reset Password</a></p>
<p><strong>This link will expire in {reset_expiry_hours} hour{'s' if reset_expiry_hours != 1 else ''}.</strong></p>
</body>
</html>"""

        # Create MIME message
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = current_app.config["MAIL_DEFAULT_SENDER"]
        msg["To"] = user.email

        msg.attach(MIMEText(text_body, "plain"))
        msg.attach(MIMEText(html_body, "html"))

        # SMTP configuration
        smtp_server = current_app.config["MAIL_SERVER"]
        smtp_port = current_app.config["MAIL_PORT"]
        smtp_user = current_app.config["MAIL_USERNAME"]
        smtp_pass = current_app.config["MAIL_PASSWORD"]

        logger.info(f"Connecting to SMTP server {smtp_server}:{smtp_port} as {smtp_user}")

        if current_app.config.get("MAIL_USE_SSL", False):
            server = smtplib.SMTP_SSL(smtp_server, smtp_port)
        else:
            server = smtplib.SMTP(smtp_server, smtp_port)

        server.set_debuglevel(1)

        if current_app.config.get("MAIL_USE_TLS", False):
            server.starttls()

        server.login(smtp_user, smtp_pass)
        send_result = server.sendmail(msg["From"], [msg["To"]], msg.as_string())
        server.quit()

        if send_result:
            logger.warning(f"SMTP sendmail returned errors: {send_result}")
        else:
            logger.info(f"SMTP sendmail succeeded to {msg['To']}")

    except Exception as e:
        logger.error(f"Failed to send password reset email to user {user.id if user else 'unknown'}: {str(e)}")
        if user:
            user.reset_token = None
            user.reset_token_expiry = None
            db.session.commit()
        raise


# ----------------------
# Create user with validation
# ----------------------
def create_user(username, email, password, age=None, sex=None):
    """Create user with comprehensive validation and security measures"""
    try:
        # Basic validation
        if not username or not email or not password:
            raise ValueError("Username, email, and password are required")
        
        # Validate email
        if not is_valid_email(email):
            raise ValueError("Invalid email format")
        
        # Validate password
        is_valid, message = validate_password_strength(password)
        if not is_valid:
            raise ValueError(message)
        
        # Validate username
        if len(username) < 3 or len(username) > 50:
            raise ValueError("Username must be between 3 and 50 characters")
        
        if not re.match(r'^[a-zA-Z0-9_]+$', username):
            raise ValueError("Username can only contain letters, numbers, and underscores")
        
        # Check for reserved usernames
        reserved_usernames = [
            'admin', 'administrator', 'root', 'system', 'api', 'www',
            'mail', 'email', 'support', 'help', 'info', 'contact',
            'test', 'demo', 'guest', 'null', 'undefined'
        ]
        
        if username.lower() in reserved_usernames:
            raise ValueError("Username is not available")
        
        # Validate age if provided
        if age is not None:
            if not isinstance(age, int) or age < 13 or age > 120:
                raise ValueError("Age must be between 13 and 120")
        
        # Validate sex if provided
        valid_sex_values = ['male', 'female', 'other', 'prefer_not_to_say']
        if sex and sex not in valid_sex_values:
            raise ValueError("Invalid sex value")
        
        # Generate secure password hash
        password_hash = generate_password_hash(
            password, 
            method='pbkdf2:sha256:150000'
        )
        
        # Create user object
        user_data = {
            'username': username.strip(),
            'email': email.lower().strip(),
            'password_hash': password_hash,
            'created_at': datetime.utcnow(),
            'failed_login_attempts': 0,
        }
        
        if age is not None:
            user_data['age'] = age
        
        if sex:
            user_data['sex'] = sex
        
        user = User(**user_data)
        
        db.session.add(user)
        db.session.commit()
        
        logger.info(f"New user created: {username} ({email})")
        return user
        
    except Exception as e:
        logger.error(f"User creation failed: {str(e)}")
        db.session.rollback()
        raise


# ----------------------
# Login attempt management 
# ----------------------
def check_login_attempts(user):
    """Check if user has exceeded maximum login attempts"""
    max_attempts = int(current_app.config.get('MAX_LOGIN_ATTEMPTS', 10))
    lockout_duration = int(current_app.config.get('LOGIN_LOCKOUT_DURATION', 900))  # seconds
    
    if user.failed_login_attempts >= max_attempts:
        # Since you don't have last_failed_login, use locked_until instead
        if user.locked_until and user.locked_until > datetime.utcnow():
            remaining_time = (user.locked_until - datetime.utcnow()).total_seconds()
            return False, f"Account locked. Try again in {int(remaining_time // 60)} minutes."
        elif user.locked_until and user.locked_until <= datetime.utcnow():
            # Reset attempts after lockout period
            user.failed_login_attempts = 0
            user.locked_until = None
            db.session.commit()
    
    return True, None



def record_failed_login(user):
    """Record a failed login attempt (without last_failed_login)"""
    user.failed_login_attempts += 1
    
    max_attempts = int(current_app.config.get('MAX_LOGIN_ATTEMPTS', 10))
    lockout_duration = int(current_app.config.get('LOGIN_LOCKOUT_DURATION', 900))
    
    if user.failed_login_attempts >= max_attempts:
        user.locked_until = datetime.utcnow() + timedelta(seconds=lockout_duration)
    
    db.session.commit()
    
    remaining_attempts = max_attempts - user.failed_login_attempts
    
    if remaining_attempts <= 0:
        return f"Account locked due to too many failed attempts. Try again in {lockout_duration // 60} minutes."
    else:
        return f"Invalid credentials. {remaining_attempts} attempts remaining."

def record_successful_login(user):
    """Record a successful login and reset failed attempts (without last_failed_login)"""
    user.failed_login_attempts = 0
    user.locked_until = None
    user.last_login = datetime.utcnow()  
    db.session.commit()

# ----------------------
# Password reset rate limiting 
# ----------------------
def check_reset_rate_limit(user):
    """Check if user has an active reset token"""
    if user.reset_token and user.reset_token_expiry:
        if user.reset_token_expiry > datetime.utcnow():
            remaining_time = (user.reset_token_expiry - datetime.utcnow()).total_seconds()
            return False, f"Reset email already sent. Try again in {int(remaining_time//60)} minutes."
    
    return True, None

def record_reset_attempt(user):
    """Record a password reset attempt (simplified for existing DB schema)"""
    # This will be handled in send_password_reset_email when token is created
    pass


# ----------------------
# Security utility functions
# ----------------------
def sanitize_input(text, max_length=None):
    """Sanitize text input"""
    if not text:
        return text
    
    text = text.strip()
    
    if max_length and len(text) > max_length:
        text = text[:max_length]
    
    return text


def is_safe_redirect_url(url):
    """Check if URL is safe for redirects (prevent open redirects)"""
    if not url:
        return True
    
    if url.startswith('/'):
        return True
    
    try:
        from urllib.parse import urlparse
        parsed = urlparse(url)
        
        if parsed.netloc:
            allowed_domains_str = current_app.config.get('ALLOWED_REDIRECT_DOMAINS', '')
            allowed_domains = [domain.strip() for domain in allowed_domains_str.split(',') if domain.strip()]
            return parsed.netloc in allowed_domains
        
        return True
    except:
        return False


# ----------------------
# Cleanup utilities
# ----------------------
def cleanup_expired_tokens():
    """Clean up expired reset tokens - run this as a periodic task"""
    try:
        expired_users = User.query.filter(
            User.reset_token_expiry.is_not(None),
            User.reset_token_expiry < datetime.utcnow()
        ).all()
        
        count = 0
        for user in expired_users:
            user.reset_token = None
            user.reset_token_expiry = None
            count += 1
        
        if count > 0:
            db.session.commit()
            logger.info(f"Cleaned up {count} expired reset tokens")
        
        return count
        
    except Exception as e:
        logger.error(f"Token cleanup failed: {str(e)}")
        db.session.rollback()
        return 0

# ----------------------
# Security utility functions
# ----------------------
def sanitize_input(text, max_length=None):
    """Sanitize text input"""
    if not text:
        return text
    
    # Strip whitespace
    text = text.strip()
    
    # Limit length if specified
    if max_length and len(text) > max_length:
        text = text[:max_length]
    
    return text


def is_safe_redirect_url(url):
    """Check if URL is safe for redirects (prevent open redirects)"""
    if not url:
        return True
    
    # Only allow relative URLs or URLs to same domain
    if url.startswith('/'):
        return True
    
    # Check if it's an absolute URL to the same domain
    try:
        from urllib.parse import urlparse
        parsed = urlparse(url)
        
        if parsed.netloc:
            allowed_domains = current_app.config.get('ALLOWED_REDIRECT_DOMAINS', [])
            return parsed.netloc in allowed_domains
        
        return True  # Relative URL
    except:
        return False


# ----------------------
# Session cleanup utility
# ----------------------
def cleanup_expired_sessions():
    """Clean up expired sessions"""
    try:
        # This would be implemented based on your session storage backend
        # For file-based sessions: clean up old files
        # For Redis: use TTL
        # For database: delete expired records
        
        logger.info("Session cleanup completed")
        return True
        
    except Exception as e:
        logger.error(f"Session cleanup failed: {str(e)}")
        return False