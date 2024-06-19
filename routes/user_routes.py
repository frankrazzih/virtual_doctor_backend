'''routes for user operations'''

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
    create_mail_object,
    get_cur_time
    )
from sqlalchemy.orm import join
#create a blueprint
user_bp = Blueprint('user', __name__)

#registration endpoint
@user_bp.route('/register', methods=['POST', 'GET'])
def register():
    if request.method == 'POST':
        #collects the user registration details and save to the db
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        email = request.form['email']
        contact = request.form['contact']
        birthday = request.form['birthday']
        gender = request.form['gender']
        password = request.form['password']
        #hash the password
        hashed_pwd = hash_pwd(password)
        #create a new user
        new_user = Users(
            first_name = first_name,\
            last_name = last_name,\
            email = email,\
            contact = contact,\
            birthday = birthday,\
            gender = gender,\
            password = hashed_pwd,\
            user_uuid = gen_uuid(),\
            reg_date = get_cur_time()
        )

        try:
            db.session.add(new_user)
            db.session.commit()
            # #send an email to the user confirming registration
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
            return render_template('/private/user_portal/user_sign_in.html')
        #errors arising due to unique constraint violation
        except:
            db.session.rollback()
            flash('Number or email already exists!')
            return render_template('/public/sign_in.html')
        finally:
            db.session.close()
    else:
        #render the registration page
        return render_template('/private/user_portal/user_sign_up.html')

#sign_in endpoint
@user_bp.route('/sign_in', methods=['POST', 'GET'])
def sign_in():
    """checks if the enterd password matches the one 
    stored in the database for the customer
    """
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        hashed_pwd = db.session.query(Users.password).filter_by(email=email).first()
        if hashed_pwd is not None:
            correct_pwd = check_pwd(password, hashed_pwd[0])
        else:
            flash('Email does not exist!. Please try again.')
            return render_template('/private/user_portal/user_sign_in.html')
        if correct_pwd:
            #store user id in the session
            user = db.session.query(Users).filter_by(email=email).first()
            session['user_uuid'] = user.user_uuid
            session['user']
            return render_template('/private/user_portal/user_home.html')
        else:
            flash('Wrong password!. Please try again.')
            return render_template('/private/user_portal/user_sign_in.html')
    elif request.method == 'GET':
        #if method is GET
        return render_template('/private/user_portal/user_sign_in.html')

#logout
@user_bp.route('/logout', methods=['GET'])
def logout():
    '''logout a user'''
    del session['user_uuid'] #remove a user's uuid from the session
    return redirect(url_for('public.home'))

#user homepage
@user_bp.route('/home', methods=['GET'])
def home():
    '''user homepage'''
    if 'user_uuid' in session:
        return render_template('/private/user_portal/user_home.html')
    else:
        return redirect(url_for('public.home'))

#booking
@user_bp.route('/booking', methods=['POST', 'GET'])
def booking():
    '''booking endpoint'''
    data = None
    if request.method == 'GET':
        return render_template('/private/user_portal/booking.html')
    #search operation
    if request.form.get('action') != 'booking':
        service = request.form.get('service')
        hosp = request.form.get('hospital')
        #if hosp is none, user is searching all hospitals
        if not hosp:
            res: list[tuple] = db.session.query(Staff, Hospitals, Services)\
                            .join(Hospitals, Staff.hosp_id == Hospitals.hosp_id)\
                            .join(Services, Staff.service == Services.service)\
                            .filter(Staff.service == service)\
                            .filter(Staff.availability == True).all()
            data = None
            if res:
                data: list[tuple] = [(hosp.hosp_name, staff.staff_name, staff.availability, staff.service, service.cost) for staff, hosp, service in res]
            return render_template('/private/user_portal/booking.html', data=data, method='post', data_content='all')
        else:
            #searching for a specific hospital
            res: tuple = db.session.query(Staff, Hospitals)\
                            .join(Hospitals, Staff.hosp_id == Hospitals.hosp_id)\
                            .filter(Staff.service == service)\
                            .filter(Staff.availability == True)\
                            .filter(Hospitals.hosp_name == hosp).first()
            data = None
            if res:
                data: tuple = (res[1].hosp_name, res[0].staff_name, res[0].availability, res[0].service)
            return render_template('/private/user_portal/booking.html', data=data, method='post', data_content='one')
    #booking operation
    else:
        service = request.form.get('service')
        hospital = request.form.get('hospital')
        staff = request.form.get('staff')
        availability = request.form.get('availability')
        booking_uuid = gen_uuid() #track unlogged in users
        session['booking_uuid'] = booking_uuid
        #check if user is logged in
        if 'user_uuid' in session:
            new_booking = Bookings(
                booking_uuid = booking_uuid,
                service = service,
                date = get_cur_time(),
                cost = cost
            )


        
