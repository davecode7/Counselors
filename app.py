from flask import Flask, request,  jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import os



app = Flask(__name__)


#database structure
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
    
    #this only accept a json not a form
    data = request.get_json()
    
    firstname = data.get('fname')
    lastname = data.get('lname')
    email = data.get('email')
    password = data.get('password')

    #this checks if the user filled all sections and if yes the user logs in successfully
    if (firstname and lastname and email and password):
        return jsonify({'message': 'user registered successfully'}), 201
    
    
    #checks if all fields are not field, if not throws the bellow error
    if not any ([firstname, lastname, email, password]):
        return jsonify({'message': 'Empty fields, fill up the fields'}), 400

    
    #stores empty fields then through an error of each
    missing_fields = []

    if not firstname:
        missing_fields.append('firstname')
    if not lastname:
        missing_fields.append('lastname')
    if not email:
        missing_fields.append('email')
    if not password:
        missing_fields.append('password')

    if missing_fields:
        return jsonify({'error': f'Missing fields: {", ".join(missing_fields)}'}), 400

    

    #Check if email already exists
    existing_user = User.query.filter_by(email=email).first()
    if existing_user:
        return jsonify({"error": "Email already registered"}), 409
    
    
    
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







