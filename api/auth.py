'''Verifirs the login credentials and createa an access token if successful'''
from models.models import (
    Patients,
    Hospitals,
    Doctors,
    Pharmacy,
    db
)
from flask_jwt_extended import create_access_token, jwt_required, get_current_user
from flask import request, jsonify, Blueprint, current_app

auth_bp = Blueprint('auth', __name__)

@auth_bp('/login/<string: role>', methods=['POST'])
def login(role):
    payload = request.get_json('')
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
        res = user.check_pwd(pwd, user.password)
    except:
        current_app.logger.error(f'An error occured while querying the table {table}', exc_info=True)
        return 'An error occured', 500
    if res:
        #create token
        token = create_access_token(identity=email, role=role)
        return jsonify(
            {
                'status': 'OK',
                'token': token
                }), 200
    else:
        return 'Unauthorized', 401   