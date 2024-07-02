'''creating and handling of virtual meetings'''

from flask import (
    Blueprint, 
    render_template, 
    request,
    jsonify,
    session,
    redirect,
    url_for,
    flash)
from .utils import (
    hash_pwd,
    check_pwd,
    gen_uuid,
    send_email,
    get_cur_time,
    clear_session_except,
    redis_client
    )
from models import(
    Bookings,
    Prescriptions,
    db
)
from dotenv import load_dotenv
import os
import jwt
import datetime
import requests
import json
from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound

meeting_bp = Blueprint('meeting', __name__)

api_key = os.getenv('API_KEY')
secret = os.getenv('SECRET')

def gen_token():
    '''create access token'''
    load_dotenv()
    expiration_in_seconds = 7200
    expiration = datetime.datetime.now() + datetime.timedelta(seconds=expiration_in_seconds)
    token = jwt.encode(payload={
	    'exp': expiration,
	    'apikey': api_key,
	    'permissions': ['allow_join'], # 'ask_join' || 'allow_mod' 
	    'version': 2, #OPTIONAL
    },  key=secret, algorithm= 'HS256')
    return token

def create_room():
    '''create a meeting room'''
    url = "https://api.videosdk.live/v2/rooms"
    token = gen_token()
    headers = {'Authorization' : token,'Content-Type' : 'application/json'}
    room_id = None
    try:
        response = requests.post(url, json={}, headers=headers)
        response = response.json()
        room_id = response.get('roomId')
    except Exception as error:
        print(error)
    return room_id

class MeetingNotFoundError(Exception):
    '''custom class for handling non existent meetings'''
    pass

class TokenNotFoundError(Exception):
    '''custom class for handling non existent tokens'''
    pass

def get_payload(token: str)->dict:
    '''get a payload from a jwt'''
    if not token:
        raise TokenNotFoundError('Token is required to access the meeting')
    payload = jwt.decode(token, os.getenv('APP_KEY'), algorithms=['HS256'])
    return payload

def get_meeting_info(hash_name: str, key: str)->dict:
    '''get the meeting info'''
    #check if meeting_id is in pending meetings
    meeting_info = redis_client.hget(hash_name, key)
    if not meeting_info:
        raise MeetingNotFoundError('Meeting does not exist!')
    #retrieve the meeting information
    meeting_info = json.loads(meeting_info.decode('UTF-8'))
    return meeting_info

#check if both parties have joined the meeting
patient_access = False
staff_access = False

@meeting_bp.route('/', methods=['GET'])
def meeting():
    '''start the meeting'''
    #retrieve payload and verify the token
    token = request.args.get('token')
    try:
        payload = get_payload(token)
        start_time = payload['start_time']
        meeting_id = str(payload['meeting_id'])
        owner = payload['owner']
    except TokenNotFoundError as error:
        flash(str(error))
        return redirect(url_for('public.home'))
    except jwt.InvalidTokenError:
        flash('Invalid meeting token')
        return redirect(url_for('public.home'))
    #check timing of the meeting
    if start_time != 'immediate':
        # Convert start_time to a datetime.time object
        start_time_obj = datetime.datetime.strptime(start_time, '%H:%M').time()
        if get_cur_time().time() < start_time_obj:
            #return back to the requesting page
            flash(f'Meeting has not yet started. It will start at {start_time}')
            return redirect(url_for('public.home'))
    #check if meeting_id is in pending meetings
    try:
        meeting_info = get_meeting_info('pending_meetings', meeting_id)
    except MeetingNotFoundError as error:
        flash(str(error))
        return redirect(url_for('public.home'))
    user_uuid = meeting_info.get('user_uuid')
    user_id = meeting_info.get('user_id')
    staff_uuid = meeting_info.get('staff_uuid')
    booking_uuid = meeting_info.get('booking_uuid')
    #add meeting to active meetings
    meeting_info = json.dumps({
                'booking_uuid': booking_uuid,
                'staff_uuid': staff_uuid,
                'user_uuid': user_uuid,
                'user_id': user_id,
                'start_time': str(get_cur_time().time())
            })
    redis_client.hset('active_meetings', meeting_id, meeting_info)
    #remove the meeting from the pending meetings
    #check if both patient and staff have accessed the meeting to clear it from the pending meetings
    global staff_access
    global patient_access
    if owner == 'staff':
        staff_access = True
    else:
        patient_access = True
    if staff_access is True and patient_access is True:
        redis_client.hdel('pending_meetings', meeting_id)
    #patient return url
    link = os.getenv('LINK')
    make_token = lambda payload: jwt.encode(payload, os.getenv('APP_KEY'), algorithm='HS256')
    payload = {
        'meeting_id': meeting_id,
        'owner': 'patient'
        }
    patient_ret_url = f'{link}/meeting/finished?token={make_token(payload)}'
    #staff return url
    payload['owner'] = 'staff'
    staff_ret_url = f'{link}/meeting/finished?token={make_token(payload)}'
    #render the meeting page with respective return url
    if owner == 'patient':
       return render_template('/public/meeting.html', meeting_id=meeting_id, api_key=api_key, ret_url=patient_ret_url)
    else:
        return render_template('/public/meeting.html', meeting_id=meeting_id, api_key=api_key, ret_url=staff_ret_url)
    
#check if both parties have ended the meeting
fin_patient_access = False
fin_staff_access = False

@meeting_bp.route('/finished', methods=['GET'])
def finished():
    '''handle completed meetings'''
    #retrieve and verify the token
    token = request.args.get('token')
    payload = get_payload(token)
    try:
        meeting_id = payload['meeting_id']
        owner = payload['owner']
    except jwt.InvalidTokenError:
        flash('Invalid meeting token')
        return redirect(url_for('public.home'))
    #check if meeting_id is in active meetings
    meeting_info = get_meeting_info('active_meetings', meeting_id)
    user_uuid = meeting_info.get('user_uuid')
    user_id = meeting_info.get('user_id')
    staff_uuid = meeting_info.get('staff_uuid')
    booking_uuid = meeting_info.get('booking_uuid')
    start_time = meeting_info.get('start_time')
    end_time = get_cur_time().time()
    #update the details of the booking
    try:
        booking = db.session.query(Bookings).filter(Bookings.booking_uuid==booking_uuid).first()
        booking.started = start_time
        booking.ended = end_time
        booking.complete = True
        db.session.commit()
    except Exception as error:
        db.session.rollback()
        print(error)
    #remove the meeting from active meetings
    #check if both patient and staff have ended the meeting to clear it from the active meetings
    global fin_patient_access
    global fin_staff_access
    if owner == 'staff':
        fin_staff_access = True
    else:
        fin_patient_access = True
    if fin_staff_access is True and fin_patient_access is True:
        redis_client.hdel('active_meetings', meeting_id)
        fin_patient_access = False
        fin_staff_access = False
    #reset the access to allow other meetings
    #save relevant details to track prescription
    presc_uuid = gen_uuid()
    if owner == 'staff':
        #issue prescription and consultation report
        session['pending_presc'] = {
            'user_id': user_id,
            'presc_uuid': presc_uuid
        }
        flash('Meeting is over. Log in to your portal to issue report and consultation immediately')
        return redirect(url_for('public.sign_in', portal='staff'))
    else:
        session['pending_presc'] = presc_uuid
        flash('Meeting is over. Please login to your portal to receive prescription and report.')
        return redirect(url_for('public.sign_in', portal='user'))
