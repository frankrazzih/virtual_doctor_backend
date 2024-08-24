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
from .schema import validate_schema
from marshmallow import ValidationError
from datetime import datetime
import json
from .utils import (
    gen_uuid,
    get_cur_time,
    pre_process_file,
    send_email,
    create_random_pwd,
    create_csrf_token,
)
from csrf import csrf

auth_bp = Blueprint('auth', __name__)

def check_schema(payload: dict, activity: str)->dict:
    '''validates the schema'''
    schema = validate_schema(activity)
    try:
        schema.load(payload)
    except ValidationError as err:
        return {
                'error':{
                    'type': 'ValidationError',
                    'message': err.messages
                }
            }

@csrf.exempt
@auth_bp.route('/register/<string:role>', methods=['POST'])
def register(role):
    '''user registration endpoint'''
    #retrieve payload depending on role
    if role == 'patient':
        payload = request.get_json()
        user = Patients
    elif role == 'hospital' or role == 'pharmacy':
        if role == 'hospital':
            user = Hospitals
        else:
            user = Pharmacy
        #check if a file exists
        files = request.files.getlist('files')
        if not files:
            return jsonify({
                'error': 'No file was uploaded'
            }), 400
        payload = json.loads(request.form.get('payload'))
    else:
        return jsonify({
            'error': 'Invalid request'
        }), 400
    
    #validate payload
    validation_err = check_schema(payload, 'register')
    if validation_err:
        return jsonify({
            'error': 'Invalid email or password format'
        }), 400
    
    #add users
    role = payload['role']
    name = payload['name']
    email = payload['email']
    contact = payload['contact']
    #check if user exists
    user_exists = db.session.query(user).filter_by(email=email).first()
    if user_exists:
        return jsonify({
            'error': 'User already exists. Login instead'
        }), 409
    if role == 'patient':
        new_user = Patients(
            patient_uuid = gen_uuid(),
            name = name,
            email = email,
            contact = contact,
            birthday = payload['birthday'],
            gender = payload['gender'],
            reg_date = get_cur_time()
        )
        new_user.set_pwd(payload['pwd'])
    if role == 'hospital':
        new_user = Hospitals(
            hosp_uuid = gen_uuid(),
            hosp_name = name,
            hosp_address = payload['address'],
            contact = contact,
            email = email,
        )
        #one time pwd to be issued after the hospital has been verified
        new_user.set_pwd(create_random_pwd())
    elif role == 'pharmacy':
        new_user = Pharmacy(
            pharm_uuid = gen_uuid(),
            pharm_name = name,
            pharm_address = payload['address'],
            contact = contact,
            email = email,
        )
        #one time pwd to be issued after the pharmacy has been verified
        new_user.set_pwd(create_random_pwd)
    try:
        db.session.add(new_user)
        db.session.commit()
    except:
        db.session.rollback()
        current_app.logger.error(f'{role} registration failed', exc_info=True)
        return jsonify({
            'error': 'An error occured. Please try again'
        }), 500
    
    #save the files for hospital and pharmacy
    if role != 'patient':
        try:
            for file in files:
                pre_process_file(file, role, name)
        except:
            current_app.logger.error(f'File for {role} not saved', exc_info=True)
            return jsonify({
                'error': 'An error occured while processing the file. Please upload the documents again'
            }), 500
        #create email body for pharmacy and hospital
        body = f'Your registration documents have been received. We will verfiy them and\
            get back to you as soon as possible. Thank you for considering to offer your services through us.'
    else:
        #create email body for patients
        body = f'Thank you for registering with Virtual Doctor..\
            We ensure you get quality healthcare anywhere anytime.\
                Your doctor is a few clicks away. Feel free to reach out incase of any issues.'
    
    #send email
    subject = 'Virtual Doctor registration'
    recipients = [email]
    send_email(subject, recipients, body)
    return jsonify(
        {
            'message': 'Regisration successful',
            'role': role
        }
    ), 201

@csrf.exempt
@auth_bp.route('/login/<string:role>', methods=['POST'])
def login(role):
    '''user login endpoint'''
    payload = request.get_json()

    #check the role to define table name
    if role == 'patient':
        user = Patients
    elif role == 'doctor':
        user = Doctors
    elif role == 'hospital':
        user = Hospitals
    elif role == 'pharmacy':
        user = Pharmacy
    else:
        return jsonify({
            'error': 'Invalid role'
        }), 400
    
    #validate payload
    validation_err = check_schema(payload, 'login')
    if validation_err:
        current_app.logger.error(f'Validation error on login: {validation_err}')
        return jsonify({
            'error': 'Invalid email or password. Please try again'
        }), 400
    
    #verify login credentials
    email = payload.get('email')
    pwd = payload.get('pwd')
    try:
        #check if user exists
        available_user = db.session.query(user).filter_by(email=email).first()
        if not available_user:
            return jsonify({
                'error': 'Invalid email or password',
            }
            ), 404
        
        #verify password
        correct_pwd = available_user.check_pwd(pwd, available_user.password)
        if not correct_pwd:
            return jsonify({
                'error': 'Invalid email/password'
            }), 401
    except:
        current_app.logger.error(f'An error occured while querying the table {user}', exc_info=True)
        return jsonify({
            'error': 'An error occured! Please try again'
        }), 500
    
    #create auth tokens token
    jwt_token = create_access_token(identity={
        'email': email,
        'role': role
    })
    csrf_token = create_csrf_token()
    # response.set_cookie('auth_token', token, secure=True, samesite='Lax')
    # response.set_cookie('csrf_token', token, secure=True, samesite='Lax')
    response.set_cookie('jwt_token', jwt_token)
    response.set_cookie('csrf_token', csrf_token)
    response = make_response({
        'role': role,
        'message': 'Login successful',
        })
    return response, 200