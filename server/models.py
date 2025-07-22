from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)    
    firstname = db.Column(db.String(50),)
    lastname = db.Column(db.String(50),)
    email = db.Column(db.String(150), unique=True,)
    password = db.Column(db.String(300),)


class Add(db.Model):
    id = db.Colum(db.Integer, primary_key=True)
    Full_Name = db.Column(db.String(50),)
    email = db.Column(db.String(50),)
    password = db.Column(db.String(300),)