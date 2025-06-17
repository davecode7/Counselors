from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import os



app = Flask(__name__)



app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///mindspace.db'
db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)    
    firstname = db.Column(db.String(50), nullable=False)
    lastname = db.Column(db.String(50),  nullable=False)
    email = db.Column(db.String(150), unique=True,  nullable=False)
    password = db.Column(db.String(150), nullable=False)


@app.route('/register', methods=['POST'])
def register():
    data = register.form
    firstname = data.get('fname')
    lastname = data.get('lname')
    email = data.get('email')
    password = data.get('password')

    
    
    if not (firstname and lastname and email and password):
        return jsonify({'error': 'all fields must be field'}),400
    
    #hash the password, making it invisible
    hashed_password = generate_password_hash(password)



    #saves user info in the database
    new_user = User(firstname=firstname, lastname=lastname, email=email, password=hashed_password)
    db.session.add(new_user)
    db.session.commit()
     
    new_user = User(firstname=firstname, lastname=lastname, email=email, password=hashed_password)
    db.session.add(new_user)
    db.session.commit()




if __name__ == '__main__':
    #this allows sqlalchemy to find data and create data according to your db.Model
    with app.app_context():
        db.create_all()
    app.run(debug=True)







