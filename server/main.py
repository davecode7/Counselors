from flask import Flask
from flask_jwt_extended import JWTManager
from flask_sqlalchemy import SQLAlchemy
from server.models import db, User
import pymysql

pymysql.install_as_MySQLdb()
from dotenv import load_dotenv
import os
load_dotenv()


from authentication.auth import authentication


app = Flask(__name__)

# JWT Secret Key
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY')

#setting up MySQL connection
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initializing extensions
db.init_app(app)

# Enable JWT authentication for this app
jwt = JWTManager(app)  

# Registering Blueprints, helps organize all related routes in the blueprint
app.register_blueprint(authentication, url_prefix='/auth')

# Create all tables
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True)




