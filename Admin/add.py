from flask import Flask, request, jsonify, Blueprint
from flask_jwt_extended import create_access_token, set_access_cookies, get_jwt_identity, get_jwt, verify_jwt_in_request
from server.models import db, Add
from datetime import timezone, timedelta, datetime
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

Admin = Blueprint('Admin', '__name__')

# Define how early before expiration you want to refresh the token
REFRESH_WINDOW_MINUTES = 60
#Refreshing token  
@Admin.after_request
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



@Admin.route('/up', methods=['POST'])
def up():
    data = request.get_json()
    Full_Name = data.get('Full_Name')
    email = data.get('email')
    password = data.get('password')

    Missing_fields = []
    if not Full_Name:
        Missing_fields.append('Full_Name')
    if not email:
        Missing_fields.append('email')
    if not password:
        Missing_fields.append('password')
    
    if Missing_fields:
        return jsonify({f'Erro, Missing_fields', {Missing_fields}}), 400
    

    existing_user = Admin.query.filter_by(email=email).first()
    if existing_user:
        return jsonify({'Email already exist'}), 400
    

    hashed_password = generate_password_hash(password)

    new_user = Admin(Full_Name=Full_Name, email=email, password=hashed_password)
    db.session.add(new_user)
    db.session.commit()
    return jsonify({'Account created successfully'}), 201


@Admin.route('/log', methods=['POST'])
def log():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    Missing_fields = []
    if not email:
        Missing_fields.append('email')
    if not password:
        Missing_fields.append('password')

    user = Admin.query.filter_by(email=email).first()
    if not user:
        return jsonify({'message': 'Invalid email'}), 400
    
    if check_password_hash(user.password, password):
        pass
        return jsonify({'message': 'Invalid password'}), 400

    access_token = create_access_token(identity=email)
    response = jsonify({
        'message':'Account created sucessfully',
        'access_token': access_token
    })
    set_access_cookies(response, access_token)
    return response, 201
