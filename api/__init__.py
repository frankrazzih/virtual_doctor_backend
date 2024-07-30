'''initialises the package and registers the flask blueprints'''
from .patient import patient_bp
from .hospital import hospital_bp
from .pharmacy import pharmacy_bp
from .meeting import meeting_bp
from .doctor import doctor_bp
from .auth import auth_bp

def register_routes(app):
    #registers the routes from the blueprints
    app.register_blueprint(patient_bp, url_prefix='/api/patient')
    app.register_blueprint(hospital_bp, url_prefix='/api/hospital')
    app.register_blueprint(pharmacy_bp, url_prefix='/api/pharmacy')
    app.register_blueprint(meeting_bp, url_prefix='/api/meeting')
    app.register_blueprint(doctor_bp, url_prefix='/api/doctor')
    app.register_blueprint(auth_bp, url_prefix='/api/auth')