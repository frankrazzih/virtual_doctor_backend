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
from models.models import (
    db,
    Patients,
    Hospitals,
    Doctors,
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
from .meeting import create_room
from sqlalchemy.orm import join
#create a blueprint
doctor_bp = Blueprint('doctor', __name__)

@doctor_bp.route('/', methods=['GET', 'POST'])
def home():
    '''route for staff homepage operations'''
    if request.method == 'GET':
        #get meeting link
        url = None
        try:
            url=(redis_client.get('staff_url').decode('UTF-8'))
        except Exception as error:
            print(error)
        return render_template('/private/staff_portal/staff_home.html', url=url)
    else:
        pass
@doctor_bp.route('/sign_in', methods=['POST'])
def login():
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
        session['hosp_id'] = staff.hosp_id
        #check if the staff has a prescription to issue from a completed meeting
        make_presc = False
        if 'pending_presc' in session:
            #make the form appear in the staff portal
            make_presc = True
            flash('Please issue the prescription and report immediately')
        else:
            flash('You have successfully logged in')
        return render_template('/private/staff_portal/staff_home.html', name=staff.staff_name, make_presc=make_presc)
    else:
        flash('Wrong password!. Please try again.')
        return redirect(url_for('public.sign_in', portal='staff'))

#logout
@doctor_bp.route('/logout', methods=['GET'])
def logout():
    '''logout a staff'''
    session.clear()
    return redirect(url_for('public.home'))