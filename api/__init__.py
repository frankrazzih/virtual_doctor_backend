'''initialises the package and registers the flask blueprints'''
from .patient import patient_bp
from .hospital import hospital_bp
from .pharmacy import pharmacy_bp
from .meeting import meeting_bp
from .doctor import doctor_bp

def register_routes(app):
    #registers the routes from the blueprints
    app.register_blueprint(patient_bp, url_prefix='/patient')
    app.register_blueprint(hospital_bp, url_prefix='/hospital')
    app.register_blueprint(pharmacy_bp, url_prefix='/pharmacy')
    app.register_blueprint(meeting_bp, url_prefix='/meeting')
    app.register_blueprint(doctor_bp, url_prefix='/doctor')