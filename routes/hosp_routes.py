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
    Staff,
    Services
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
            return redirect(url_for('public.sign_in', portal='hospital'))
        #errors arising due to unique constraint violation
        except:
            db.session.rollback()
            flash('Number or email already exists!')
            return render_template('/private/hospital_portal/hospital_sign_up.html')
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
    if not hosp:
        flash('Email does not exist!. Please try again.')
        return redirect(url_for('public.sign_in', portal='hospital'))
    hashed_pwd = hosp.password
    if hashed_pwd is not None:
        correct_pwd = check_pwd(password, hashed_pwd)
    if correct_pwd:
        session['hosp_id'] = hosp.hosp_id
        session['hosp_uuid'] = hosp.hosp_uuid
        return redirect(url_for('hospital.home'))
    else:
        flash('Wrong password!. Please try again.')
        return redirect(url_for('public.sign_in', portal='hospital'))
    
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
@hospital_bp.route('/staff', methods=['POST'])
def staff():
    '''register the hospitals staff'''
    counter = 1
    while True:
        staff_name = request.form.get(f'staff{counter}')
        service = request.form.get(f'service{counter}')
        contact = request.form.get(f'contact{counter}')
        email = request.form.get(f'email{counter}')
        counter += 1
        #all entries have been got
        if staff_name is None or service is None or contact is None or email is None:
            flash('Staff upload was successful!')
            return redirect(url_for('hospital.home'))
        new_staff = Staff(
            staff_uuid = gen_uuid(),
            staff_name = staff_name,
            email = email,
            contact = contact,
            service = service,
            hosp_id = session['hosp_id']
        )
        try:
            db.session.add(new_staff)
            db.session.commit()
        except Exception as error:
            print(error)
            flash('An error occured please try again!')
            return redirect(url_for('hospital.home'))

#register services
@hospital_bp.route('/services', methods=['POST'])
def services():
    '''register the services offered by the hospital'''
    counter = 1
    while True:
        service = request.form.get(f'service{counter}')
        cost = request.form.get(f'cost{counter}')
        counter += 1
        #all entries have been got
        if service is None or cost is None:
            flash('Services upload was successful!')
            return redirect(url_for('hospital.home'))
        new_service = Services(
            cost = cost,
            service = service,
            hosp_id = session.get('hosp_id')
        )
        try:
            db.session.add(new_service)
            db.session.commit()
        except Exception as error:
            print(error)
            flash('An error occured please try again!')
            return redirect(url_for('hospital.home'))
        

