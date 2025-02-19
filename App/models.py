from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import URLSafeTimedSerializer

db = SQLAlchemy()

class User(db.Model, UserMixin):
    user_id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())

    animals = db.relationship('Animal', backref='owner', lazy=True)

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)

    def get_reset_token(self, expires_sec=1800):
        s = URLSafeTimedSerializer(app.config['SECRET_KEY'])
        return s.dumps({'user_id': self.user_id})

    @staticmethod
    def verify_reset_token(token):
        s = URLSafeTimedSerializer(app.config['SECRET_KEY'])
        try:
            user_id = s.loads(token)['user_id']
        except:
            return None
        return User.query.get(user_id)

    def get_id(self):
        return str(self.user_id)  # Pastikan mengembalikan ID sebagai string
    

class Animal(db.Model):
    hewan_id = db.Column(db.Integer, primary_key=True)
    nama = db.Column(db.String(100), nullable=False)
    jenis = db.Column(db.String(50), nullable=False)
    umur = db.Column(db.Integer, nullable=False)
    pemilik_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), nullable=False)
    tanggal_masuk = db.Column(db.DateTime, default=db.func.current_timestamp())