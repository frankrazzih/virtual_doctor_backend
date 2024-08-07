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
from .utils import (
    gen_uuid,
    get_cur_time
)

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    payload = request.get_json()
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
    email = payload['contact']
    contact = payload['contact']
    if role == 'patient':
        new_patient = Patients(
            patient_uuid = gen_uuid(),
            name = name,
            email = email,
            contact = contact,
            birthday = payload['birthday'],
            gender = payload['gender'],
            reg_date = get_cur_time()
        )
        new_patient.set_pwd(payload['pwd'])
    address = payload['address']
    if role == 'hospital':
        new_hosp = Hospitals(
            hosp_uuid = gen_uuid(),
            hosp_name = name,
            hosp_address = address,
            contact = contact,
            email = email,
        )
        new_hosp.set_pwd(random.randint(000000, 999999))
    elif role == 'pahrmacy':
        new_pharm = Pharmacy(
            pharm_uuid = gen_uuid(),
            pharm_name = name,
            pharm_address = address,
            contact = contact,
            email = email,
        )
        new_pharm.set_pwd(random.randint(000000, 999999))

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