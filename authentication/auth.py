from flask import Flask, request,  jsonify, Blueprint
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token, set_access_cookies, get_jwt_identity, get_jwt, verify_jwt_in_request
import os
from server.models import db, User
from datetime import datetime, timezone, timedelta
from flask_jwt_extended import jwt_required
from authentication.decoration import role_required
import random
import string

#traces an error if any error occur
#import pdb; pdb.set_trace()

authentication = Blueprint('authentication', '__name__')
 
# Define how early before expiration you want to refresh the token
REFRESH_WINDOW_MINUTES = 60
#Refreshing token  
@authentication.after_request
def refresh_expiring_jwts(response):
    try:
        #verify if jwt is valid
        verify_jwt_in_request(optional=True) 

        #asking when the token is going to expire
        exp_timestamp = get_jwt()["exp"]
        
        #asking what time is it
        now = datetime.now(timezone.utc)
        
        #looking ahead 60 minutes from now
        target_timestamp = datetime.timestamp(now + timedelta(minutes=REFRESH_WINDOW_MINUTES))
        
        #asking if the key will espire in that 60 minutes
        if target_timestamp > exp_timestamp:
            
            #then set a new key and save in cookies
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


    def generate_anonymous_username():
        while True:
            random_part = ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))
            username = f"user_{random_part}"
            # Ensure it's unique
            existing_user = User.query.filter_by(username=username).first()
            if not existing_user:
                return username
            
            #break

        


   #saves user info in the database
    new_user = User(firstname=firstname, lastname=lastname, email=email,
                     password=hashed_password, username=generate_anonymous_username())
    db.session.add(new_user)
    db.session.commit()
    return jsonify({'message': 'Account created successfully'}), 201
     



#log in code
@authentication.route('/login', methods=['POST'])
def login():
    
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

     #FIX THIS   
    Missing_fields = []
    if not email:
            Missing_fields.append('email')
    if not password:
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
         'access_token': access_token})
    set_access_cookies(response, access_token)
    return response, 201


@authentication.route('/email_update', methods=['PUT'])
@jwt_required()
@role_required("user")
def email_update():
     
    current_email = get_jwt_identity()
    get_email = User.query.filter_by(email=current_email).first()

    if not get_email:
        return jsonify({'message': 'user could not be found'}), 400
     
    data = request.get_json()
    new_email = data.get('new_email')

    if not new_email:
         return jsonify({'message': 'new email required'}), 400

    get_email.email = new_email
    db.session.commit()
    return jsonify({'message': 'email updated successfully'}), 201


@authentication.route('/update_password', methods=['PUT'])
@jwt_required()
@role_required("user")
def update_password():
    current_email = get_jwt_identity()
    password_info = User.query.filter_by(email=current_email).first()

    if not password_info:
         return jsonify({'message': 'user could not be found'}), 400
    
    data = request.get_json()
    old_password = data.get('old_password')
    new_password = data.get('new_password')

    if not new_password or not old_password:
        return jsonify({'message': 'Both new and old password must be provided'}), 400
    
    if not check_password_hash(password_info.password, old_password):
        return jsonify({'message': 'old password is incorrect'}), 401
    
    password_info.password = generate_password_hash(new_password)
    db.session.commit()
    return jsonify({'message': 'password updated successfully'}), 201


@authentication.route('/delete', methods=['DELETE'])
@jwt_required()
@role_required("user")
def delete():
     
     current_email = get_jwt_identity()
     delete_account = User.query.filter_by(email=current_email).first()

     if not current_email:
          return jsonify({"message": "user not found"}), 400
     
     data = request.get_json()
     remove_email = data.get("remove_email")
     remove_password = data.get("remove_password")

     if not remove_email or not remove_password:
          return jsonify({"message": "Both credentials must be provided"}), 400
     
     if not check_password_hash(delete_account.password, remove_password):
          return jsonify({"message": "Invalid password"}), 400
          
     delete_account.email = generate_password_hash(remove_email)
     db.session.delete(delete_account)
     db.session.commit()
     return jsonify({"message": f"user {delete_account} has been deleted"}), 201

         
#TEST THIS ROUTE AND ADD THE RBAC TO THE ADMIN AND

