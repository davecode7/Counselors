from flask import Flask, request,  jsonify, Blueprint, response
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token, set_access_cookies, get_jwt_identity, get_jwt
import os
from server.models import db, User
from datetime import datetime, timezone, timedelta

authentication = Blueprint('authentication', '__name__')
 
# Define how early before expiration you want to refresh the token
REFRESH_WINDOW_MINUTES = 60
#Refreshing token  
@authentication.after_request
def refresh_expiring_jwts(response):
    try:
        exp_timestamp = get_jwt()["exp"]
        now = datetime.now(timezone.utc)
        target_timestamp = datetime.timestamp(now + timedelta(minutes=REFRESH_WINDOW_MINUTES))
        if target_timestamp > exp_timestamp:
            access_token = create_access_token(identity=get_jwt_identity())
            set_access_cookies(response, access_token)
        return response
    except (RuntimeError, KeyError):
      #return response if jwt is invalid
        return response




@authentication.route('/signup', methods=['POST'])
def register():
    
    #this only accept a json not a form
    data = request.get_json()
    firstname = data.get('firstname')
    lastname = data.get('lastname')
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
@authentication.route('/login', methods=['POST'])
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
        return jsonify({'message': 'Invalid email'}), 400
    
    #hashes the entered password and comapare it to the hash password in the db
    if check_password_hash(existing_user.password, password):
        pass
    else:
        return jsonify({'message': 'Invalid password'}), 401
        
        
    
    
    #create an access token for the user to verify their identity when visiting a protected route
    access_token = create_access_token(identity=email)
    response = jsonify({
         'msg': 'logged in successfully',
         'access_token': access_token
         }), 201
    set_access_cookies(response, access_token)
    return response


