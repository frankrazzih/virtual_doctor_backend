#!/usr/bin/env python3
'''entry point to the program
creates app and runs it'''
from routes import register_routes
from flask import Flask

def create_app():
    '''configure the app from different modules'''
    app = Flask(__name__)
    register_routes(app)

    return app

#create the app
app = create_app()

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)