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
    clear_session_except
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
            #send an email to the user confirming registration
            subject = 'VIRTUAL DOCTOR REGISTRATION'
            recipients = [email]
            body = 'Thank You for registering with Virtual Doctor!\nQuality healthcare anywhere, anytime.'
            send_email(subject, recipients, body)
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

# sign_in endpoint
@user_bp.route('/sign_in', methods=['POST'])
def sign_in():
    """Checks if the entered password matches the one stored in the database for the customer"""
    email = request.form['email']
    password = request.form['password']
    user = db.session.query(Users).filter_by(email=email).first()
    
    if user:
        hashed_pwd = user.password
        correct_pwd = check_pwd(password, hashed_pwd)
        
        if correct_pwd:
            # Store user id in the session
            session['user_uuid'] = user.user_uuid
            session['user_id'] = user.user_id
            
            # Check if user has a booking id to resume booking
            if session.get('booking_uuid') is not None:
                return redirect(url_for('user.finish_booking'))
            
            flash(f'Successfully logged in as {user.first_name} {user.last_name}')
            return redirect(url_for('user.home'))
        else:
            flash('Wrong password! Please try again.')
    else:
        flash('Email does not exist! Please try again.')

    return render_template('/private/user_portal/user_sign_in.html')

#logout
@user_bp.route('/logout', methods=['GET'])
def logout():
    '''logout a user'''
    session.clear()
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
    if request.method == 'GET':
        return render_template('/private/user_portal/booking.html')
    data = None
    hosp_id = None
    #search operation
    if request.form.get('action') == 'searching':
        service = request.form.get('service')
        hosp = request.form.get('hospital')
        #if hosp is none,
        if not hosp:
            #get all hospitals offering the services
            all_res: list[tuple] = db.session.query(Services, Hospitals)\
                            .join(Hospitals, Services.hosp_id == Hospitals.hosp_id)\
                            .filter(Services.service == service)\
                            .all()
            if all_res:
                data: list[tuple] = [(hosp.hosp_name, service.service, service.cost, hosp.hosp_id) for service, hosp in all_res]
            return render_template('/private/user_portal/booking.html', data=data, method='post', data_content='all')
        else:
            #searching for a specific hospital
            one_res: tuple = db.session.query(Services, Hospitals)\
                            .join(Hospitals, Services.hosp_id == Hospitals.hosp_id)\
                            .filter(Services.service == service)\
                            .filter(Hospitals.hosp_name == hosp).first()
            if one_res:
                data: tuple = (one_res[1].hosp_name, one_res[0].service, one_res[0].cost, one_res[1].hosp_id)
            return render_template('/private/user_portal/booking.html', data=data, method='post', data_content='one')
    #booking operation
    elif request.form.get('action') == 'booking':
        service = request.form.get('service')
        hosp_name = request.form.get('hosp_name')
        price = request.form.get('price')
        hosp_id = request.form.get('hosp_id')
        #get the available staff for that service
        av_staff = db.session.query(Staff)\
                            .filter(Staff.hosp_id == hosp_id)\
                            .filter(Staff.availability == True)\
                            .first()
        if av_staff:
            staff_avail_time = av_staff.availability
            staff_id = av_staff.staff_id
            staff_name = av_staff.staff_name
        else:
            flash('No doctor is currently available. Please try another hospital.')
            return redirect(url_for('user.booking'))
        booking_uuid = gen_uuid() #track unlogged in users
        session['booking_uuid'] = booking_uuid
        #store all details in the session
        session['service'] = service
        session['hosp_name'] = hosp_name
        session['price'] = price
        session['hosp_id'] = hosp_id
        session['staff_name'] = staff_name
        session['staff_id'] = staff_id
        session['staff_avail_time'] = staff_avail_time
        #check if user is logged in
        if 'user_uuid' in session:
            return redirect(url_for('user.finish_booking'))
        else:
            return redirect(url_for('user.sign_in'))

#finish booking
@user_bp.route('/finish_booking', methods=['GET', 'POST'])
def finish_booking():
    if request.method == 'GET':
        #retun the booking details for the user to confirm
        return render_template('/private/user_portal/finish_booking.html', 
                               hosp_name=session.get("hosp_name"), 
                               staff_name=session.get("staff_name"),
                                 service=session.get("service"), 
                                 staff_av=session.get("staff_avail_time"),
                                   price=session.get("price"))
    
    else:
        #complete booking
        action = request.form.get('booking_action')
        if action == 'cancel':
            #remove booking details from the session
            clear_session_except(session, 'user_id', 'user_uuid')
            flash('You have cancelled your booking!')
            return redirect(url_for('user.home'))
        elif action == 'confirm':
            #store booking details in the booking table
            new_booking = Bookings(
                booking_uuid = session.get('booking_uuid'),
                service = session.get('service'),
                date = get_cur_time(),
                cost = session.get('price'),
                complete = False,
                user_id = session.get('user_id'),
                hosp_id = session.get('hosp_id'),
                staff_id = session.get('staff_id')
            )
            try:
                db.session.add(new_booking)
                db.session.commit()
                #send email to hosp and user notifying them of the booking
                #clear the session
                clear_session_except(session, 'user_id', 'user_uuid')
                flash('Booking was successful!')
                return redirect(url_for('user.home'))
            except:
                flash('Booking failed! Try again.')
                redirect(url_for('user.booking'))

