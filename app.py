#!/usr/bin/env python3
'''entry point to the program
creates app and runs it'''
from api import register_routes
from flask import Flask
from models.models import db
from dotenv import load_dotenv
import os
from flask_migrate import Migrate
from flask_mail import Mail
from log_conf import logger
from flask_talisman import Talisman
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_wtf.csrf import CSRFProtect

csrf = None

def create_app():
    '''configure the app from different modules'''
    app = Flask(__name__)

    load_dotenv() #load the env variables
    #secure app
    app.secret_key = os.getenv('APP_KEY')
    # Set up JWT
    app.config['JWT_SECRET_KEY'] = os.environ.get('JWT_SECRET_KEY')
    app.config['JWT_TOKEN_LOCATION'] = ['cookies']
    #app.config['JWT_COOKIE_SECURE'] = True
    app.config['JWT_ACCESS_COOKIE_PATH'] = '/'
    #app.config['JWT_COOKIE_CSRF_PROTECT'] = True  # Enable CSRF protection for cookies
    JWTManager(app)

    #serve the app over https only
    # talisman = Talisman(app, content_security_policy=None)

    CORS(app)
    global csrf
    csrf = CSRFProtect(app)

    #setup logging
    try:
        app.logger = logger
        app.logger.info('Logging setup successfully')
    except:
        app.logger.warning(f'Logging setup failed!', exc_info=True)
        raise

    #create upload directories
    try:
        app.config['UPLOAD_FOLDER'] = os.path.join(app.root_path, 'uploads')
        #verification directories
        pharmacy_dir = os.path.join(app.config['UPLOAD_FOLDER'], 'pharmacy')
        hospital_dir = os.path.join(app.config['UPLOAD_FOLDER'], 'hospital')
        #prescriptions directories 
        prescription_dir = os.path.join(app.config['UPLOAD_FOLDER'], 'prescriptions')

        # Ensure the directories exist
        for dir in [app.config['UPLOAD_FOLDER'], pharmacy_dir, hospital_dir, prescription_dir]:
            if not os.path.exists(dir):
                os.makedirs(dir)
        app.logger.info('Uploads directory set up successfully')
    except:
        app.logger.critical('Uploads directory not set up', exc_info=True)
        raise
    
    #configure the db
    try:
        db_pwd = os.getenv('DB_PASSWORD')
        db_user = os.getenv('DB_USER')
        db_host = os.getenv('DB_HOST')
        app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql+pymysql://{db_user}:{db_pwd}@{db_host}/virtual_doctor'
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        app.logger.info('DataBase set up successfully')
    except:
        app.logger.critical(f'An error occurred while setting up the database!', exc_info=True)
        raise

    #initialise db and set up migration
    try:
        db.init_app(app)
        #create the database
        with app.app_context():
            db.create_all()
        Migrate(app, db)
        app.logger.info('Migrations set up successfully')
    except:
        app.logger.warning(f'Migration set up failed!', exc_info=True)
        raise

    #register blueprints
    try:
        register_routes(app)
        app.logger.info('Blueprints registered successfully')
    except:
        app.logger.critical(f'Blueprints registration failed!', exc_info=True)
        raise
    
    #configure mail server
    try:
        app.config['MAIL_SERVER'] = os.getenv('MAIL_SERVER')
        app.config['MAIL_PORT'] = os.getenv('MAIL_PORT')
        app.config['MAIL_USE_TLS'] = True
        app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
        app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')
        Mail(app)
        app.logger.info('Mail service setup successfully')
    except:
        app.logger.critical(f'Mail service setup failed!', exc_info=True)
        raise
    
    return app

#create the app
try:
    app = create_app()
    app.logger.info('App created successfully')
except:
    app.logger.critical(f'App was not created!',  exc_info=True)
    raise

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
    #port=443, ssl_context=('cert.pem', 'key.pem')
