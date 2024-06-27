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
from dotenv import load_dotenv
import os
import jwt
import datetime
import requests

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
    meeting_id = create_room()
    return render_template('/public/meeting.html', meeting_id=meeting_id, api_key=api_key)