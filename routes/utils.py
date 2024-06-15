'''utility functions'''
import bcrypt
import uuid
from flask_mail import Mail
import importlib
from datetime import datetime

#create a mail object
def create_mail_object():
    '''return a mail object'''
    app_file = importlib.import_module('app')
    mail = Mail(app_file.app)
    return mail

def hash_pwd(password: str)->bytes:
    '''hash the password with a salt'''
    pwd_bytes = password.encode('UTF-8')
    salt = bcrypt.gensalt()
    hashed_pwd = bcrypt.hashpw(pwd_bytes, salt)
    return hashed_pwd

def check_pwd(password: str, hashed_pwd: bytes)->bool:
    '''checks whether a password is correct'''
    pwd_bytes = password.encode('UTF-8')
    hashed_pwd = hashed_pwd.encode('UTF-8')
    return bcrypt.checkpw(pwd_bytes, hashed_pwd)

def gen_uuid()->uuid:
    '''generates a uuid'''
    return str(uuid.uuid4())

def get_cur_time():
    '''returns current time'''
    return datetime.now()