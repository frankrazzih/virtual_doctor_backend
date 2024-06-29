'''utility functions'''
import bcrypt
import uuid
from flask_mail import Mail, Message
import importlib
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
import redis

executor = ThreadPoolExecutor() #to create a separate thread to send the email
#set redis client
redis_client = redis.StrictRedis(host='localhost', port=6379, db=0)

#async email function
def send_async_mail(app, msg: Mail):
    #send email asynchronously
    with app.app_context():
        mail = Mail(app)
        mail.send(msg)

#async email function
def send_email(subject: str, recipients: list[str], body: str):
    '''prepare to send email asynchronously with flask mail'''
    app_file = importlib.import_module('app')
    app = app_file.app
    msg = Message(subject, sender='naismart@franksolutions.tech', recipients=recipients)
    msg.body = body
    executor.submit(send_async_mail, app, msg)

#hash password
def hash_pwd(password: str)->bytes:
    '''hash the password with a salt'''
    pwd_bytes = password.encode('UTF-8')
    salt = bcrypt.gensalt()
    hashed_pwd = bcrypt.hashpw(pwd_bytes, salt)
    return hashed_pwd

#check hashed password
def check_pwd(password: str, hashed_pwd: bytes)->bool:
    '''checks whether a password is correct'''
    pwd_bytes = password.encode('UTF-8')
    hashed_pwd = hashed_pwd.encode('UTF-8')
    return bcrypt.checkpw(pwd_bytes, hashed_pwd)

#generate uuid
def gen_uuid()->uuid:
    '''generates a uuid'''
    return str(uuid.uuid4())

#get current time
def get_cur_time():
    '''returns current time'''
    return datetime.now()

#clear session keys except the one needed
def clear_session_except(session, key1, key2, key3):
    keys_to_remove = [key for key in session.keys() if (key != key1 and key != key2 and key != key3)]
    for key in keys_to_remove:
        session.pop(key, None)