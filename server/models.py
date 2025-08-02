from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)    
    firstname = db.Column(db.String(50),)
    lastname = db.Column(db.String(50),)
    email = db.Column(db.String(150), unique=True,)
    password = db.Column(db.String(300),)
    role = db.Column(db.String(20), default="user", nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class Therapy(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    Full_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True,  nullable=False)
    password = db.Column(db.String(100), nullable=False)
    my_id = db.Column(db.String(100), unique=True, nullable=False)
    role = db.Column(db.String(20), default="counselor", nullable=False)
    Create_at = db.Column(db.DateTime, default=datetime.utcnow)

