'''routes for user operations'''

from flask import (
    current_app,
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
    Services,
    Prescriptions,
    Medicine,
    Stock,
    Pharmacy,
    Pharm_orders
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
import json
from os import getenv
import jwt
from sqlalchemy import or_
from sqlalchemy.sql import func, distinct
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
            current_app.logger.info('User registration successful')
            #send an email to the user confirming registration
            subject = 'VIRTUAL DOCTOR REGISTRATION'
            recipients = [email]
            body = 'Thank You for registering with Virtual Doctor!\nQuality healthcare anywhere, anytime.'
            send_email(subject, recipients, body)
            flash('Registration was successful')
            return redirect(url_for('public.sign_in', portal='user'))
        #errors arising due to unique constraint violation
        except:
            db.session.rollback()
            current_app.logger.error('Patirnt registation failed', exc_info=True)
            flash('Number or email already exists!')
            return render_template('/private/user/user_sign_up.html')
    else:
        #render the registration page
        return render_template('/private/user_portal/user_sign_up.html')

# sign_in endpoint
@user_bp.route('/sign_in', methods=['POST'])
def sign_in():
    """Checks if the entered password matches the one stored in the database for the customer"""
    email = request.form['email']
    password = request.form['password']
    try:
        user = db.session.query(Users).filter_by(email=email).first()
    except:
        current_app.logger.error('An error occured while querying for a patient by email', exc_info=True)
    if user:
        hashed_pwd = user.password
        correct_pwd = check_pwd(password, hashed_pwd)
        
        if correct_pwd:
            # Store user details in the session
            session['user_uuid'] = user.user_uuid
            session['user_id'] = user.user_id
            session['email'] = user.email
            session['user_name'] = user.first_name + user.last_name
            # Check if user has a booking id to resume booking
            if 'booking_uuid' in session:
                return redirect(url_for('user.finish_booking'))
            #check if user has an active prescription
            get_presc = False
            if 'presc_uuid' in session:
                get_presc = True
                flash('Your prescription is being prepared by your doctor.\n\
                      It will be available in a few minutes')
            else:
                flash(f'Successfully logged in as {user.first_name} {user.last_name}')
            return render_template('/private/user_portal/user_home.html', get_presc=get_presc)
        else:
            flash('Wrong password! Please try again.')
            return redirect(url_for('public.sign_in', portal='user'))
    else:
        flash('Email does not exist! Please try again.')
        return redirect(url_for('public.sign_in', portal='user'))

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
        # #check if user has a pending prescription
        # if session.get('pending_presc') == session['user_uuid']:
        #     presc = 
        return render_template('/private/user_portal/user_home.html')
    else:
        return redirect(url_for('public.sign', portal='user'))

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
            try:
                all_res: list[tuple] = db.session.query(Services, Hospitals)\
                                .join(Hospitals, Services.hosp_id == Hospitals.hosp_id)\
                                .filter(Services.service == service)\
                                .all()
            except:
                current_app.logger.error('An error occured when querying for all hospitals offering a certain service', exc_info=True)
            if all_res:
                data: list[tuple] = [(hosp.hosp_name, service.service, service.cost, hosp.hosp_id) for service, hosp in all_res]
            return render_template('/private/user_portal/booking.html', data=data, method='post', data_content='all')
        else:
            #searching for a specific hospital
            try:
                one_res: tuple = db.session.query(Services, Hospitals)\
                                .join(Hospitals, Services.hosp_id == Hospitals.hosp_id)\
                                .filter(Services.service == service)\
                                .filter(Hospitals.hosp_name == hosp).first()
            except:
                current_app.logger.error('An error occured when querying a specific hospital offering a certain service', exc_info=True)
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
        try:
            av_staff = db.session.query(Staff)\
                            .filter(Staff.hosp_id == hosp_id)\
                            .filter(Staff.availability == True)\
                            .first()
        except:
            current_app.logger.error('An error ocurred when querying available staff', exc_info=True)
        if av_staff:
            staff_avail_time = av_staff.availability
            staff_id = av_staff.staff_id
            staff_name = av_staff.staff_name
            staff_uuid = av_staff.staff_uuid
            staff_email = av_staff.email
        else:
            flash('No doctor is currently available. Please try another hospital.')
            return redirect(url_for('user.booking'))
        #track unlogged in users
        session['booking_uuid'] = gen_uuid()
        #store all details in the session
        session['service'] = service
        session['hosp_name'] = hosp_name
        session['price'] = price
        session['hosp_id'] = hosp_id
        session['staff_name'] = staff_name
        session['staff_id'] = staff_id
        session['staff_avail_time'] = staff_avail_time
        session['staff_uuid'] = staff_uuid
        session['staff_email'] = staff_email
        #check if user is logged in
        if 'user_uuid' in session:
            return redirect(url_for('user.finish_booking'))
        else:
            return redirect(url_for('public.sign_in', portal='user'))

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
        sch_time = request.form.get('consultation_time')
        session_keys_to_keep = ['user_id', 'user_uuid', 'email', 'user_name']
        if sch_time == 'immediate':
            #create the meeting immediately
            time = None
            time_link = sch_time
        else:
            #schedule the meeting to start at the specified time
            time = request.form.get('scheduled_time')
            time_link = time
        if action == 'cancel':
            #remove booking details from the session
            clear_session_except(session, session_keys_to_keep)
            flash('You have cancelled your booking!')
            return redirect(url_for('user.home'))
        elif action == 'confirm':
            #store booking details in the booking table
            booking_uuid = session.get('booking_uuid')
            new_booking = Bookings(
                booking_uuid = booking_uuid,
                service = session.get('service'),
                date = get_cur_time(),
                scheduled_time = time,
                cost = session.get('price'),
                user_id = session.get('user_id'),
                hosp_id = session.get('hosp_id'),
                staff_id = session.get('staff_id')
            )
            try:
                db.session.add(new_booking)
                db.session.commit()
                room_id = create_room()
                #store the meeting details in redis
                try:
                    room_data = {
                            'booking_uuid': booking_uuid,
                            'staff_uuid': session['staff_uuid'],
                            'user_uuid': session['user_uuid'],
                            'user_id': session['user_id'],
                            'presc_uuid': gen_uuid()
                        }
                    redis_client.hset('pending_meetings', room_id, json.dumps(room_data))
                except Exception as error:
                    print(f'redis error: {error}')
                #create meeting links
                link = getenv('LINK')
                payload = {
                    'meeting_id': room_id,
                    'start_time': time_link,
                    'owner': 'patient'
                }
                make_token = lambda payload: jwt.encode(payload, getenv('APP_KEY'), algorithm='HS256')
                #create a secure token with the payload
                token = make_token(payload)
                user_url = f'{link}/meeting?token={token}'
                #send booking confrimation and meeting links
                #user email
                subject = 'VIRTUAL DOCTOR BOOKING CONFIRMATION'
                recipients = [session['email']]
                body = f'You appointment with doctor {session["staff_name"]}\n\
                    Start time: {sch_time}\n\
                    Meeting link: {user_url}\n\
                    Please keep time.'
                send_email(subject, recipients, body)
                #staff email
                payload = {
                    'meeting_id': room_id,
                    'start_time': time_link,
                    'owner': 'staff'
                }
                token = make_token(payload)
                staff_url = f'{link}/meeting?token={token}'
                subject = 'VIRTUAL DOCTOR APPOINTMENT NOTIFICATION'
                recipients = [session['staff_email']]
                body = f'You have been been booked for a consultation with {session["user_name"]}\n\
                    Start time: {sch_time}\n\
                    Meeting link: {staff_url}\n\
                    Please keep time.'
                send_email(subject, recipients, body)
                #display joining links on respective portals
                redis_client.set('staff_url', staff_url)
                #remove booking details from the session
                clear_session_except(session, session_keys_to_keep)
                flash('Booking was successful!')
                return render_template('/private/user_portal/user_home.html', url=user_url)
            except Exception as error:
                print('Error: ', error)
                db.session.rollback()
                flash('Booking failed! Try again.')
                return redirect(url_for('user.booking'))

@user_bp.route('/presc', methods=['GET', 'POST'])
def presc():
    '''manage the users prescriptions'''
    #store prescriptions issued by staff
    if request.method == 'POST':
        #check if doctor has pending presc
        if 'pending_presc' not in session:
            flash('No pending prescriptions to issue')
            return redirect(request.referrer)
        #retrieve and save the prescription issued to redis and database
        counter = 1
        report = request.form.get('report')
        med_entries = [] #list of medicine entries
        while True:
            med_name = request.form.get(f'med_name{counter}')
            dosage = request.form.get(f'dosage{counter}')
            inst = request.form.get(f'inst{counter}')
            counter += 1
            #check if all info has been retrieved
            if not med_name:
                break
            med_entries.append({
                'med_name': med_name,
                'dosage': dosage,
                'inst': inst
            })
        presc = {
            'report': report,
            'prescriptions': med_entries
        }
        pending_presc = session['pending_presc']
        presc_uuid = pending_presc['presc_uuid']
        try:
            #store in redis temporarily
            redis_client.setex(presc_uuid, 600 ,json.dumps(presc))
            #store to db
            new_presc = Prescriptions(
                presc_uuid = presc_uuid,
                date_issued = get_cur_time(),
                report = report,
                prescription = json.dumps(med_entries),
                staff_id = session['staff_id'],
                hosp_id = session['hosp_id'],
                status = 'incomplete',
                user_id = pending_presc['user_id']
            )
            db.session.add(new_presc)
            db.session.commit()
        except Exception as error:
            current_app.logger.error(error, exc_info=True)
        #clear pending prescription from the session
        del session['pending_presc']
        flash('Prescription and report were issued successfully')
        return redirect(url_for('staff.home'))
    else:
        #retrieve prescriptions for the user
        presc = None
        presc_uuid = session['presc_uuid']
        try:
            presc = redis_client.get(presc_uuid)
            if not presc:
                flash('Prescription is not available. Please try again after a few minutes')
                return render_template('/private/user_portal/user_home.html', get_presc=True)
        except Exception as error:
            current_app.logger.error(error, exc_info=True)
        presc = json.loads(presc.decode('UTF-8'))
        del session['presc_uuid']
        return render_template('/private/user_portal/user_home.html', presc=presc, presc_uuid=presc_uuid)
    
@user_bp.route('/pharm_search', methods=['GET', 'POST'])
def pharm_search():
    '''purchase medicine from the pharmacy'''
    if request.method == 'GET':
        '''return pharmacy page'''
        if 'page' in request.args:
            return redirect(url_for('public.sign_in'))
        return render_template('/private/user_portal/pharm_orders.html', step1=True)
    else:
        #check if the presc is will be retrieved using the presc_uuid or from a prescription uploaded
        presc_uuid = request.form.get('presc_uuid')
        med_entries = []
        if not presc_uuid:
            #data is sent through an uploaded prescrition so retrieve it
            counter = 1
            while True:
                med_name = request.form.get(f'med_name{counter}')
                dosage = request.form.get(f'dosage{counter}')
                counter += 1
                #check if all entries have been retrieved
                if not med_name:
                    current_app.logger.info('Uploaded prescription retrieved')
                    break
                med_entries.append(
                    {
                        'med_name': med_name,
                        'dosage': dosage
                    }
                )
        else:
            #check if the presc exists in memory
            try:
                presc = redis_client.get(presc_uuid)
                #missing presc due to expiry or does not exist
                if not presc:
                    #check for the prescription in db
                    try:
                        presc = db.session.query(Prescriptions).filter_by(presc_uuid=presc_uuid).first()
                        #presc does not exist in either db or memory
                        if not presc:
                            flash('Prescription not found!')
                            return redirect(request.referrer)
                        #extract the prescription details
                        med_entries = json.loads(presc.prescription)
                        current_app.logger.info('prescription retrieved from prescriptions database')
                    except:
                        current_app.logger.error(f'An error occured when retrieving prescription from db', exc_info=True)
                else:
                    #extract the prescription details from redis
                    decoded_presc = json.loads(presc.decode('UTF-8'))
                    med_entries = decoded_presc['prescriptions']
                    #remove the presc from redis
                    redis_client.delete(presc_uuid)
                    current_app.logger.info('Prescription retrieved from redis and memory freed')
            except:
                current_app.logger.error(f'An error occured while retrieving prescription from redis', exc_info=True)
        #extract med names from med entries
        med_names = [med['med_name'] for med in med_entries]
        #create an order and store the med_entries in memory and db to be submitted to pharmacy for delivery
        order_uuid = gen_uuid()
        session['order_uuid'] = order_uuid
        try:
            redis_client.setex(order_uuid, 300, json.dumps(med_entries))
            new_order = Pharm_orders(
                order_uuid = order_uuid,
                presc = json.dumps(med_entries),
                status = 'incomplete'
            )
            db.session.add(new_order)
            db.session.commit()
        except:
            db.session.rollback()
            current_app.logger.error('An error occured while storing order details to pharm_orders', exc_info=True)
        not_av = [] #meds not found
        av_pharm = None
        #search for the meds
        try:
            med_res = db.session.query(Pharmacy,
                func.sum(Stock.price).label('total_price'),
                func.count(distinct(Stock.meds_id)).label('med_count'))\
                .join(Stock, Stock.pharm_id == Pharmacy.pharm_id)\
                .join(Medicine, Stock.meds_id == Medicine.meds_id)\
                .filter(or_(Medicine.brand_name.in_(med_names), Medicine.gen_name.in_(med_names)))\
                .filter(Stock.avail == True)\
                .group_by(Pharmacy.pharm_id).all()
            #check for pharmacies with all the med ids
            av_pharm = []
            for pharm, total_price, med_count in med_res:
                #skip pharmacies that don't have all the meds
                if med_count != len(med_names):
                    continue
                else:
                    #save the pharmacy details to be shown in the serach results
                    av_pharm.append(
                        {
                            'name': pharm.pharm_name,
                            'price': total_price,
                            'pharm_uuid': pharm.pharm_uuid
                        }
                    )
            current_app.logger.info('Prescription searched in database')
        except Exception as err:
            current_app.logger.error(f'An error occured when searching for meds in the database{err}')
        if not_av:
            return render_template('/private/user_portal/pharm_orders.html', av_pharm=av_pharm, not_av=not_av, med_entries=med_entries, step1=True)
        else:
            return render_template('/private/user_portal/pharm_orders.html', av_pharm=av_pharm, not_av=not_av, med_entries=med_entries, step2=True)

@user_bp.route('/pharm_orders', methods=['POST'])
def pharm_orders():
    '''Make orders to pharmacy for the submitted prescription'''
    pharm_uuid = request.form.get('pharm_uuid')
    order_uuid = session.get('order_uuid')
    user_id = session.get('user_id')
    if not user_id:
        flash('Please login to finish order')
        return redirect(url_for('public.sign_in', portal='user'))
    #if order uuid is not av ask the user to make order again
    if not order_uuid:
        flash('An error occurred. Please make the order again')
        return render_template('/private/user_portal/pharm_orders.html', step1=True)
    price = request.form.get('price')
    lat = request.form.get('lat')
    long = request.form.get('long')
    #process location
    if not lat or not long:
        flash('An error occurred while processing your location. Please make sure location is on in your device\
              for deliveries to be made.')
        return render_template('/private/user_portal/pharm_orders.html', step2=True)
    location = f'https://www.google.com/maps/search/?api=1&query={lat},{long}'
    #get pharm details and user details
    pharm = None
    try:
        pharm = db.session.query(Pharmacy).filter_by(pharm_uuid=pharm_uuid).first()
        user = db.session.query(Users).filter(Users.user_id == session['user_id']).first()
        if not pharm or not user:
            flash('An error occured when making the order. Please place the order again')
            return render_template('/private/user_portal/pharm_orders.html', step1=True)
    except:
        current_app.logger.warning('An error occurred when searching for the pharmacy selected or to make an order', exc_info=True)
    #retrieve the prescription
    try:
        presc = redis_client.get(session['order_uuid'])
        #retrieve the presc from db if it does not exist in memory
        if not presc:
            presc = db.session.query(Pharm_orders).filter_by(order_uuid=order_uuid).first()
            if not presc:
                flash('An error occurred. Please make the order again')
                return render_template('/private/user_portal/pharm_orders.html', step1=True)
            else:
                decoded_presc = json.loads(presc.presc)
        else:
            decoded_presc = json.loads(presc.decode('UTF-8'))
    except:
        current_app.logger.warning('An error occured while retrieving order info', exc_info=True)
        flash('An error occured while placing the order. Please place the order again')
        return render_template('/private/user_portal/pharm_orders.html', step1=True)
    #send an email to pharmacy to make the delivery
    subject = 'DELIVERY ALERT'
    recipients = [pharm.email]
    body = f'An order has been placed for the prescription below. The user details are also included\
        Make the delivery as soon as possible\n\
        Prescription:\n\
            {decoded_presc}\n\
        Total price: {price}\n\
        User details:\n\
        \t Contact: {user.contact}\n\
        \t Location: {location}'
    send_email(subject, recipients, body)
    current_app.logger.info('Order made successfully')
    return render_template('/private/user_portal/pharm_orders.html', step3=True)
    