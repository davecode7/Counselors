import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))



from flask import Flask
from flask_jwt_extended import JWTManager
from flask_sqlalchemy import SQLAlchemy
from server.models import db, User, Add
import pymysql

pymysql.install_as_MySQLdb()
from dotenv import load_dotenv
import os
load_dotenv()




app = Flask(__name__)

# JWT Secret Key
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'your-default-secret')

#setting up MySQL connection
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initializing extensions
db.init_app(app)
from authentication.auth import authentication
from Admin.add import Admin
from logout.log import logout

# Enable JWT authentication for this app
jwt = JWTManager(app)  

# Registering Blueprints, helps organize all related routes in the blueprint
app.register_blueprint(authentication, url_prefix='/auth')
app.register_blueprint(Admin, url_prefix='/Admin')
app.register_blueprint(logout, url_prefix='/logout')

# Create all tables
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True)




