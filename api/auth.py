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
from .schema import validate_reg_data
from marshmallow import ValidationError
from datetime import datetime
import random
import json
from .utils import (
    gen_uuid,
    get_cur_time,
    pre_process_file,
    send_email
)

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register/<string:role>', methods=['POST'])
def register(role):
    #retrieve payload depending on role
    if role == 'patient':
        payload = request.get_json()
    elif role == 'hospital' or role == 'pharmacy':
        '''check if a file exists'''
        files = request.files.getlist('files')
        if not files:
            return 'Missing file', 400
        payload = json.loads(request.form.get('payload'))
    else:
        return 'Invalid url', 400
    #validate payload
    schema = validate_reg_data()
    try:
        schema.load(payload)
    except ValidationError as err:
        return jsonify(
            {
                'error':{
                    'type': 'ValidationError',
                    'message': err.messages
                }
            }
        ), 400
    #store data
    role = payload['role']
    name = payload['name']
    email = payload['email']
    contact = payload['contact']
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
        new_user.set_pwd(random.randint(000000, 999999))
    elif role == 'pharmacy':
        new_user = Pharmacy(
            pharm_uuid = gen_uuid(),
            pharm_name = name,
            pharm_address = payload['address'],
            contact = contact,
            email = email,
        )
        #one time pwd to be issued after the pharmacy has been verified
        new_user.set_pwd(random.randint(000000, 999999))
    try:
        db.session.add(new_user)
        db.session.commit()
    except:
        db.session.rollback()
        current_app.logger.error(f'{role} registration failed', exc_info=True)
        return 'registration failed', 500
    #save the files for hospital and pharmacy
    if role != 'patient':
        try:
            for file in files:
                pre_process_file(file, role, name)
        except:
            current_app.logger.error(f'File for {role} not saved', exc_info=True)
            return 'An error occured while saving the file', 500
        #email body
        body = f'Your registration documents have been received. We will verfiy them and\
            get back to you as soon as possible. Thank you for considering to offer your services through us.'
    else:
        #email body
        body = f'Thank you for registering with Virtual Doctor..\
            We ensure you get quality healthcare anywhere anytime.\
                Your doctor is a few clicks away. Feel free to reach out incase of any issues.'
    #send email
    subject = 'Virtual Doctor registration'
    recipients = [email]
    send_email(subject, recipients, body)
    return 'registration success', 201


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