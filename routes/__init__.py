'''initialises the package and registers the flask blueprints'''
from .public_routes import public_bp
from .user_routes import user_bp
from .hosp_routes import hospital_bp
from .pharm_routes import pharmacy_bp
from .meeting_routes import meeting_bp

def register_routes(app):
    #registers the routes from the blueprints
    app.register_blueprint(public_bp, url_prefix='/public')
    app.register_blueprint(user_bp, url_prefix='/user')
    app.register_blueprint(hospital_bp, url_prefix='/hospital')
    app.register_blueprint(pharmacy_bp, url_prefix='/pharmacy')
    app.register_blueprint(meeting_bp, url_prefix='/meeting')