'''initialises the package and registers the flask blueprints'''
from .public_routes import public_bp
from flask import Blueprint

def register_routes(app):
    #registers the routes from the blueprints
    app.register_blueprint(public_bp, url_prefix='/')