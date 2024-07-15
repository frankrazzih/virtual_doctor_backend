#!/usr/bin/env python3
'''entry point to the program
creates app and runs it'''
from routes import register_routes
from flask import Flask
from models import db
from dotenv import load_dotenv
import os
from flask_migrate import Migrate
from flask_mail import Mail
from log_conf import logger
from flask_talisman import Talisman

def create_app():
    '''configure the app from different modules'''
    app = Flask(__name__)
    
    load_dotenv() #load the env variables
    #secure app
    app.secret_key = os.getenv('APP_KEY')
    # talisman = Talisman(app, content_security_policy=None) #ensure app is only served via https
    # app.config['SESSION_COOKIE_SECURE'] = True #ensure cookies are only sent via https
    # app.config['SESSION_COOKIE_HTTPONLY'] = True #prevent cookies from being manipulated with js on clientside
    
   # Set the upload folder path
    app.config['UPLOAD_FOLDER'] = os.path.join(app.root_path, 'uploads')

    # Ensure the upload folder exists
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])

    #setup logging
    try:
        app.logger = logger
        app.logger.info('Logging setup successfully')
    except:
        app.logger.warning(f'Logging setup failed!', exc_info=True)
        raise
    
    #configure the db
    try:
        db_pwd = os.getenv('DB_PASSWORD')
        db_user = os.getenv('DB_USER')
        db_host = os.getenv('DB_HOST')
        app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql+pymysql://{db_user}:{db_pwd}@{db_host}/original_virtual_doctor'
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
    
    #configure my mail server
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