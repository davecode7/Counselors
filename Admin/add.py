from flask import Flask, jsonify, Blueprint
from flask_jwt_extended import jwt_required

Admin = Blueprint('Admin', '__name__')

#Admin dashboard
@Admin.route('/dash', methods=['GET'])
@jwt_required()
def dash():
    return jsonify({"message": "welcome admin!"})



