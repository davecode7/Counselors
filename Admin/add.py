from flask import Flask, request, jsonify, Blueprint
from flask_jwt_extended import create_access_token, set_access_cookies, get_jwt_identity, get_jwt, verify_jwt_in_request, jwt_required
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
    
    existing_user = Add.query.filter_by(email=email).first()
    if existing_user:
        return jsonify({'message': 'email already exist'}), 400

    hashed_password = generate_password_hash(password)

    new_user = Add(Full_Name=Full_Name, email=email, password=hashed_password)
    db.session.add(new_user)
    db.session.commit()
    return jsonify({'message': 'Account created successfully'}), 201


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

    user = Add.query.filter_by(email=email).first()
    if not user:
        return jsonify({'message': 'Invalid email'}), 400
    
    if check_password_hash(user.password, password):
        pass
    else:
        return jsonify({'message': 'Invalid password'}), 400

    access_token = create_access_token(identity=email)
    response = jsonify({
        'message':'login sucessfully',
        'access_token': access_token
    })
    set_access_cookies(response, access_token)
    return response, 201


@Admin.route('/dash', methods=['POST'])
@jwt_required()
def dash():
    
    current_email = get_jwt_identity()
    admin = Add.query.filter_by(email=current_email).first()

    if not admin:
        return jsonify({'message': 'Access denied'}), 403
    return jsonify(logged_in_as=current_email), 200



@Admin.route('/date_up', methods=['PUT'])
@jwt_required()
def date_up():

    current_email = get_jwt_identity()
    get_user = Add.query.filter_by(email=current_email).first()

    if not get_user:
        return jsonify({'message': 'user could not be found'}), 400
    
    data = request.get_json()
    new_email = data.get('new_email')

    if not new_email:
        return jsonify({'message': 'new email must be provided'}), 400
    
    get_user.email = new_email
    db.session.commit()
    return jsonify({'message': 'email updated successfully'}), 201



@Admin.route('/date_password', methods=['PUT'])
@jwt_required()
def date_password():

    current_email = get_jwt_identity()
    re_password = Add.query.filter_by(email=current_email).first()

    if not re_password:
        return jsonify({'message': 'user could not be found'}), 400
    
    data = request.get_json()
    old_password = data.get('old_password')
    new_password = data.get('new_password')

    if not old_password or not new_password:
        return jsonify({'message': 'Both old and new password must be provided'}), 400

    if not check_password_hash(re_password.password, old_password):
        return jsonify({'message': 'old password is incorrect'}), 400

    re_password.password =  generate_password_hash(new_password)
    db.session.commit()
    return jsonify({'message': 'password updated successfully'}), 201






