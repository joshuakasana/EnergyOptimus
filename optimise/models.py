from datetime import datetime
from optimise import db, login_manager
from flask_login import UserMixin


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    last_name = db.Column(db.String(20), nullable=False)
    first_name = db.Column(db.String(20), nullable=False)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    device_id = db.Column(db.String(20), unique=True, nullable=False)
    image_file = db.Column(db.String(20), nullable=True, default='funnyCat.jpg')
    password = db.Column(db.String(60), nullable=False)
    budget = db.Column(db.Float, nullable=False, default=1)
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)

    stats = db.relationship('Stats', backref='user', lazy=True)

    def __repr__(self):
        return f"User('{self.username}', '{self.email}', '{self.image_file}')"

class Stats(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    device_id = db.Column(db.String(20), nullable=False)
    date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    temperature = db.Column(db.Float)
    humidity = db.Column(db.Float)
    light = db.Column(db.Boolean, default=False)
    motion = db.Column(db.Boolean, default=False)
    current = db.Column(db.Float)
    energy = db.Column(db.Float)
    energy_prediction = db.Column(db.Float)

    def __repr__(self):
        return f"Stats('{self.device_id}', '{self.date}')"

