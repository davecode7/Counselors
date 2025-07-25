from flask import jsonify, Blueprint
from flask_jwt_extended  import unset_jwt_cookies

logout = Blueprint('logout', __name__)

#Route for logout
@logout.route('/out', methods=['POST'])
def out():
     response = jsonify({"msg": "logout successful"})
     #this removes the jwt cookies from the user's browser, enbling them to log out
     unset_jwt_cookies(response)
     return response
