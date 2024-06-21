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

def create_app():
    '''configure the app from different modules'''
    app = Flask(__name__)
    load_dotenv() #load the env variables
    
    app.secret_key = os.getenv('APP_KEY')
    
    #configure the db
    db_pwd = os.getenv('DB_PASSWORD')
    db_user = os.getenv('DB_USER')
    db_host = os.getenv('DB_HOST')
    app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql+pymysql://{db_user}:{db_pwd}@{db_host}/original_virtual_doctor'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    #initialise db and migration
    db.init_app(app)
    migrate = Migrate(app, db)

    #register blueprints
    register_routes(app)

    #create the database
    with app.app_context():
        db.create_all()
    
    #configure my mail server
    app.config['MAIL_SERVER'] = os.getenv('MAIL_SERVER')
    app.config['MAIL_PORT'] = os.getenv('MAIL_PORT')
    app.config['MAIL_USE_TLS'] = True
    app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
    app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')
    mail = Mail(app)
    
    return app

#create the app
app = create_app()

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)