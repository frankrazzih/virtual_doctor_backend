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
from dotenv import load_dotenv
import os
import jwt
import datetime
import requests
import json

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
    try:
        response = requests.post(url, json={}, headers=headers)
    except Exception as error:
        print(error)
        exit
    response = response.json()
    room_id = response.get('roomId')
    return room_id

@meeting_bp.route('/', methods=['GET'])
def meeting():
    '''start the meeting'''
    #check if user is logged in and the meeting id matches the one in the sesssion
    staff_uuid = request.args.get('staff_uuid')
    user_uuid = request.args.get('user_uuid')
    start_time = request.args.get('start_time')
    meeting_id = request.args.get('meeting_id')
    meeting_time = False
    if start_time == 'immediate':
        meeting_time = True
    else:
        #check if the specified time has reached
        if str(get_cur_time().time()) >= start_time:
            #return back to the requesting page
            flash(f'Meeting has not yet started. It will start at {start_time}')
            return redirect(request.referrer)
        else:
            meeting_time = True
    #authenticate the meeting to start immediately
    if meeting_time:
        #check if meeting_id is in pending meetings
        pending_meets = redis_client.hgetall('pending_meetings')
        decoded_meets = {key.decode('UTF-8'): value.decode('UTF-8') for key, value in pending_meets.items()}
        if meeting_id in decoded_meets:
            meeting_info = json.loads(decoded_meets[meeting_id])
            booking_uuid = meeting_info.get('booking_uuid')
            bk_staff_uuid = meeting_info.get('staff_uuid')
            bk_user_uuid = meeting_info.get('user_uuid')
            #check whether the provided user and staff are in a booking
            if staff_uuid == bk_staff_uuid or user_uuid == bk_user_uuid:
                #add meeting to active meetings
                meeting_info = json.dumps({
                            'booking_uuid': booking_uuid,
                            'staff_uuid': staff_uuid,
                            'user_uuid': user_uuid,
                            'start_time': get_cur_time().time()
                        })
                redis_client.hset('active_meetings', meeting_id, meeting_info)
                #remove the meeting from the pending meetings
                redis_client.hdel(meeting_id)
                return render_template('/public/meeting.html', meeting_id=meeting_id, api_key=api_key)
            else:
                flash('Invalid meeting credentials!')
                return redirect(request.referrer)
        else:
            flash('Meeting does not exist!')
            return redirect(request.referrer)
