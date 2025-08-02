from flask import Flask, jsonify, Blueprint
from flask_jwt_extended import jwt_required
from authentication.decoration import role_required

Admin = Blueprint('Admin', '__name__')

#Admin dashboard
@Admin.route('/dash', methods=['GET'])
@jwt_required()
@role_required("admin")
def dash():
    return jsonify({"message": "welcome admin!"}), 200



