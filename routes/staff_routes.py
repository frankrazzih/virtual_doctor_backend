'''routes for staff operations'''

from flask import (
    Blueprint, 
    render_template, 
    request,
    jsonify,
    session,
    redirect,
    url_for,
    flash)
from models import (
    db,
    Users,
    Hospitals,
    Staff,
    Bookings,
    Services
    )
from .utils import (
    hash_pwd,
    check_pwd,
    gen_uuid,
    send_email,
    get_cur_time,
    clear_session_except,
    redis_client
    )
from .meeting_routes import create_room
from sqlalchemy.orm import join
#create a blueprint
staff_bp = Blueprint('staff', __name__)

@staff_bp.route('/', methods=['GET', 'POST'])
def home():
    '''route for staff homepage operations'''
    if request.method == 'GET':
        return render_template('/private/staff_portal/staff_home.html', url=(redis_client.get('staff_url').encode('UTF-8')))
    else:
        pass
@staff_bp.route('/sign_in', methods=['POST'])
def sign_in():
    '''staff sign in'''
    email = request.form['email']
    password = request.form['password']
    staff = db.session.query(Staff).filter_by(email=email).first()
    if not staff:
        flash('Email does not exist!. Please try again.')
        return redirect(url_for('public.sign_in', portal='staff'))
    hashed_pwd = staff.password
    if hashed_pwd is not None:
        correct_pwd = check_pwd(password, hashed_pwd)
    if correct_pwd:
        session['staff_id'] = staff.hosp_id
        session['staff_uuid'] = staff.staff_uuid
        session['staff_name'] = staff.staff_name
        flash('You have successfully logged in')
        return render_template('/private/staff_portal/staff_home.html', name=staff.staff_name)
    else:
        flash('Wrong password!. Please try again.')
        return redirect(url_for('public.sign_in', portal='staff'))