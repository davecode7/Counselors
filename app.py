from flask import Flask, request,  jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token, set_access_cookies
import os



app = Flask(__name__)


#database structure
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///mindspace.db'
db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)    
    firstname = db.Column(db.String(50),)
    lastname = db.Column(db.String(50),)
    email = db.Column(db.String(150), unique=True,)
    password = db.Column(db.String(150),)


@app.route('/signup', methods=['POST'])
def register():
    
    #this only accept a json not a form
    data = request.get_json()
    firstname = data.get('fname')
    lastname = data.get('lname')
    email = data.get('email')
    password = data.get('password')


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
    return jsonify({'message': 'Account created successfully'}), 201
     



#logged in code
@app.route('/login', methods=['POST'])
def login():
    
    data = request.get_json()
    firstname = request.get_data('fname')
    lastname = request.get_data('lname')
    email = request.get_data('email')
    password = request.get_data('password')

        
    Missing_fields = []
    
    if firstname not in db:
            Missing_fields.append('firstname')
    if lastname not in db:
            Missing_fields.append('lastname')
    if email not in db:
            Missing_fields.append('email')
    if password not in db:
            Missing_fields.append('password')

    if Missing_fields:
             jsonify({"Error": f"Missing_fields: {Missing_fields}"}), 400
        
    
    
    
    #find a user by email 
    existing_user = User.query.filter_by(email=email).first()

    if not existing_user:
        return jsonify({'message': 'User not found'}), 400
        
    
    response = jsonify({'msg': 'logged in successfully'})
    #create an access token for the user to verify their identity when visiting a protected route
    access_token = create_access_token(identity=email)
    set_access_cookies(response, access_token)
    return response



if __name__ == '__main__':
    #this allows sqlalchemy to find data and create data according to your db.Model
    with app.app_context():
        db.create_all()
    app.run(debug=True)







