'''routes for hospital pages'''

from flask import (
    Blueprint, 
    render_template, 
    request, 
    session as flask_session, 
    flash)
from werkzeug.security import (generate_password_hash, 
                               check_password_hash)
#create a blueprint
hospital_bp = Blueprint('hospital', __name__)

#sign_in endpoint
@hospital_bp.route('/sign_in', methods=['POST', 'GET'])
def sign_in():
    """checks if the enterd password matches the one 
    stored in the database for the customer
    """
    if request.method == 'POST':
        pass
    elif request.method == 'GET':
        #if method is GET
        print('USER PORTAL!!')
        return render_template('/private/hospital_portal/hospital_sign_in.html')