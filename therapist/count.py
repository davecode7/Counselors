from flask import request, Blueprint, jsonify
from flask_jwt_extended import verify_jwt_in_request, get_jwt, get_jwt_identity, create_access_token, set_access_cookies
from flask_jwt_extended import jwt_required
from datetime import datetime, timezone, timedelta
from werkzeug.security import check_password_hash, generate_password_hash
from server.models import db, Therapy
from authentication.decoration import role_required

therapist = Blueprint('therapist', '__name__')

# Define how early before expiration you want to refresh the token
REFRESH_WINDOW_MINUTES = 60
#Refreshing token  
@therapist.after_request
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
    

@therapist.route('/set_account', methods=['POST'])
def set_account():

    data = request.get_json()
    Full_name = data.get("Full_name")
    email = data.get("email")
    password = data.get("password")
    my_id = data.get("my_id")

    Missing_fields = []
    if not Full_name:
        Missing_fields.append("Full_name")
    if not email:
        Missing_fields.append("email")
    if not password:
        Missing_fields.append("password")
    if not my_id:
        Missing_fields.append("my_id")
    if Missing_fields:
        return jsonify({"message": f"missing_fields {Missing_fields}"}), 400
    
    existing_counselor = Therapy.query.filter_by(email=email).first()
    if existing_counselor:
        return jsonify({"message": "email already exist"}), 400
    
    if Therapy.query.filter_by(my_id=my_id).first():
        return jsonify({"message": "id already taken"}), 400
    
    hashed_password = generate_password_hash(password)
    
    new_counselor = Therapy(Full_name=Full_name, email=email, password=hashed_password, my_id=my_id)
    db.session.add(new_counselor)
    db.session.commit()
    return jsonify({"message": "Account created successfully"}), 201


@therapist.route('/get_in', methods=['POST'])
def get_in():

    data = request.get_json()
    email = data.get("email")
    password = data.get("password")

    Missing_fields = []
    if not email:
        Missing_fields.append("email")
    if not password:
        Missing_fields.append("password")
    if Missing_fields:
        return jsonify({"message": f"missing_fields, {Missing_fields}"}), 400
    
    existing_email = Therapy.query.filter_by(email=email).first()
    if not existing_email:
        return jsonify({"message": "Invaid email"}), 400

    if check_password_hash(existing_email.password, password):
        pass
    else:
        return jsonify({"message": "Invalid password"}), 400

    access_token = create_access_token(identity=email)
    response = jsonify({
       "message": "logged in successfully",
        "access_token": access_token})
    set_access_cookies(response, access_token)
    return response, 201


@therapist.route('/delete_count', methods=['DELETE'])
@jwt_required()
@role_required("counselor")
def delete_count():

    current_email = get_jwt_identity()
    delete_counselor = Therapy.query.filter_by(email=current_email).first()

    if not delete_counselor:
        return jsonify({"message": "user not found"}), 400
    
    data = request.get_json()
    remove_email = data.get("remove_email")
    remove_password = data.get("remove_password")

    if not remove_email or not remove_password:
        return jsonify({"message": "Both email and password are required"}), 400
    
    if not check_password_hash(delete_counselor.password, remove_password):
        return jsonify({"message": "Invalid password"}), 400
    
    delete_counselor.email = remove_email
    db.session.delete(delete_counselor)
    db.session.commit()
    return jsonify({"message": "Account deleted successfully"}), 201


@therapist.route('/update_the_pass', methods=['PUT'])
@jwt_required()
@role_required("counselor")
def update_the_password():

    current_email = get_jwt_identity()
    up_date = Therapy.query.filter_by(email=current_email).first()

    if not up_date:
        return jsonify({"message": "user not found"}), 400
    
    data = request.get_json()
    old_password = data.get("old_password")
    new_password = data.get("new_password")

    if not old_password or not new_password:
        return jsonify({"message": "Both passwords are required"}), 400
    
    if not check_password_hash(up_date.password, old_password):
        return jsonify({"message": "Invalid old password"}), 400
    
    up_date.password = generate_password_hash(new_password)
    db.session.commit()
    return jsonify({"message": "password updated successfully"}), 201



@therapist.route('/update_the_email', methods=['PUT'])
@jwt_required()
@role_required("counselor")
def update_the_email():

    current_email = get_jwt_identity()
    up_email = Therapy.query.filter_by(email=current_email).first()

    if not up_email:
        return jsonify({"message": "user not found"}), 400
    
    data = request.get_json()
    new_email = data.get("new_email")

    if not new_email:
        return jsonify({"new email required"}), 400
    
    up_email.email = new_email
    db.session.commit()
    return jsonify({"message": "email updated successfully"}), 201

    

