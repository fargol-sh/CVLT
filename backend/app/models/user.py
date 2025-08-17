from flask_login import UserMixin
from app import db
from datetime import datetime

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(128), nullable=False)
    age = db.Column(db.Integer)
    sex = db.Column(db.String(10))
    profile_photo = db.Column(db.String(200))
    reset_token = db.Column(db.String(100))
    reset_token_expiry = db.Column(db.DateTime)  
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    failed_login_attempts = db.Column(db.Integer, default=0)
    locked_until = db.Column(db.DateTime)
    last_login = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    role = db.Column(db.String(20), default='user')
    
    # Relationships
    scores = db.relationship('Score', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<User {self.username}>'
    
    def is_admin(self):
        return self.username == 'admin'
    
    def get_scores_for_test(self, test_number):
        return self.scores.filter_by(test_number=test_number).all()
    
    def has_completed_test(self, test_number):
        scores = self.get_scores_for_test(test_number)
        rounds = [score.round_number for score in scores]
        return set(range(1, 6)) == set(rounds)
    
    # Required methods for Flask-Login
    def get_id(self):
        return str(self.id)
    
    def is_authenticated(self):
        return True
    
    def is_active(self):
        return True
    
    def is_anonymous(self):
        return False
