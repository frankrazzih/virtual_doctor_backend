'''routes for public pages'''

from flask import (
    Blueprint, 
    render_template, 
    request, 
    session as flask_session, 
    flash)
from werkzeug.security import (generate_password_hash, 
                               check_password_hash)
#create a blueprint
user_bp = Blueprint('user', __name__)

#sign_in endpoint
@user_bp.route('/sign_in', methods=['POST', 'GET'])
def sign_in():
    """checks if the enterd password matches the one 
    stored in the database for the customer
    """
    if request.method == 'POST':
        pass
    elif request.method == 'GET':
        #if method is GET
        print('USER PORTAL!!')
        return render_template('/private/user_portal/user_sign_in.html')