'''Verifirs the login credentials and createa an access token if successful'''
from models.models import (
    Patients,
    Hospitals,
    Doctors,
    Pharmacy,
    db
)
from flask_jwt_extended import create_access_token, jwt_required, get_current_user
from flask import request, jsonify, Blueprint, current_app, make_response

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register/<string:role>', methods=['POST'])
def register(role):
    payload = request.get_json()
    #check the role to search the respective table
    if role == 'patient':
        table = Patients
    elif role == 'hospital':
        table = Hospitals
    elif role == 'pharmacy':
        table = Pharmacy
    else:
        return 'Bad request', 400
    try:
        

@auth_bp.route('/login/<string:role>', methods=['POST'])
def login(role):
    payload = request.get_json()
    email = payload.get('email')
    pwd = payload.get('pwd')
    #check the role to search the respective table
    if role == 'patient':
        table = Patients
    elif role == 'doctor':
        table = Doctors
    elif role == 'hospital':
        table = Hospitals
    elif role == 'pharmacy':
        table = Pharmacy
    else:
        return 'Bad request', 400
    try:
        user = db.session.query(table).filter_by(email=email).first()
        #check password
        if not user:
            return 'No user found', 404
        correct_pwd = user.check_pwd(pwd, user.password)
    except:
        current_app.logger.error(f'An error occured while querying the table {table}', exc_info=True)
        return 'An error occured', 500
    if correct_pwd:
        #create token
        token = create_access_token(identity=email, role=role)
        response = make_response({'role': role})
        response.set_cookie({'auth_token': token})
        return response, 200
    else:
        return 'Unauthorized', 401   