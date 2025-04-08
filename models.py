from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin

db = SQLAlchemy()

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)  # Unik ID for hver bruker
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(10), nullable=False)  # roller som User og Admin
    tickets = db.relationship('Ticket', backref='user', lazy=True)

class Ticket(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    tittel = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(20), default="Åpen")  # Statuser: Åpen, Behandler, Lukket, Løst
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

