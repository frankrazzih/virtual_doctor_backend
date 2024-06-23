'''routes for hospital pages'''

from flask import (
    Blueprint, 
    render_template, 
    request,
    jsonify,
    session,
    redirect,
    url_for,
    flash)
from flask_mail import Message
from models import (
    db,
    Hospitals,
    )
from .utils import (
    hash_pwd,
    check_pwd,
    gen_uuid,
    send_email,
    get_cur_time
    )
#create a blueprint
hospital_bp = Blueprint('hospital', __name__)

#registration endpoint
@hospital_bp.route('/register', methods=['POST', 'GET'])
def register():
    if request.method == 'POST':
        #collects the hospital registration details and saves to the db
        name = request.form['name']
        location = request.form['location']
        email = request.form['email']
        contact = request.form['contact']
        password = request.form['password']
        #hash the password
        hashed_pwd = hash_pwd(password)
        #create a new user
        new_hosp = Hospitals(
            hosp_name = name,\
            hosp_location = location,\
            email = email,\
            contact = contact,\
            password = hashed_pwd,\
            hosp_uuid = gen_uuid(),\
            reg_date = get_cur_time()
        )

        try:
            db.session.add(new_hosp)
            db.session.commit()
            # #send an email to the hospital confirming registration
            # mail = create_mail_object()
            # msg = Message('VIRTUAL DOCTOR REGISTRATION', sender='naismart@franksolutions.tech', recipients=[email])
            # msg.body = 'Thank You for registering with us!\nYour health matters to us'
            # mail.send(msg)
            # '''
            # #send an email to the admin informing of a new user
            # users = session.query(Customers).filter_by(email=email).first()
            # msg = Message('New user', sender='naismart@franksolutions.tech', recipients=['francischege602@gmail.com'])
            # msg.body = f'{users.first_name} {users.last_name}\n\n\n'
            # mail.send(msg)
            # '''
            flash('Registration was successful')
            return render_template('/private/hospital_portal/hospital_sign_in.html')
        #errors arising due to unique constraint violation
        except:
            db.session.rollback()
            flash('Number or email already exists!')
            return render_template('/private/hospital_portal/hospital_sign_in.html')
        finally:
            db.session.close()
    else:
        #render the registration page
        return render_template('/private/hospital_portal/hospital_sign_up.html')

#sign_in endpoint
@hospital_bp.route('/sign_in', methods=['POST'])
def sign_in():
    """checks if the enterd password matches the one 
    stored in the database for the hospital
    """
    email = request.form['email']
    password = request.form['password']
    hosp = db.session.query(Hospitals).filter_by(email=email).first()
    hashed_pwd = hosp.password
    if hashed_pwd is not None:
        correct_pwd = check_pwd(password, hashed_pwd)
    else:
        flash('Email does not exist!. Please try again.')
        return render_template('/private/hospital_portal/hospital_sign_in.html')
    if correct_pwd:
        session['hosp_id'] = hosp.hosp_id
        session['hosp_uuid'] = hosp.hosp_uuid
        return redirect(url_for('hospital.home'))
    else:
        flash('Wrong password!. Please try again.')
        return render_template('/private/hospital_portal/hospital_sign_in.html')
    
#logout
@hospital_bp.route('/logout', methods=['GET'])
def logout():
    '''logout a hospital'''
    session.clear()
    return redirect(url_for('public.home'))
    
#hospital homepage
@hospital_bp.route('/home', methods=['GET'])
def home():
    '''returns hospital portal homepage'''
    return render_template('/private/hospital_portal/hosp_home.html')

#register staff
@hospital_bp.route('/staff')
def staff():
    '''manage the hospitals staff'''
