from functools import wraps
from flask import jsonify
from flask_jwt_extended import get_jwt_identity
from server.models import User

def role_required(*allowed_roles):
    #the route being protected
    def wrapper(fn):
        #making sure the function keeps its original identity
        @wraps(fn)
        #accepting any kind of input in the decorated function
        def decorated(*args, **kwargs):
            user = User.query.filter_by(email=get_jwt_identity()).first()

            if not user:
                return jsonify({"message": "User not found"}), 404

            if not user or user.role not in allowed_roles:
                return jsonify({"message": "Access denied"}), 403

            return fn(*args, **kwargs)
        return decorated
    return wrapper