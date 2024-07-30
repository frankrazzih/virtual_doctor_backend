'''manage passwords'''
import bcrypt
from flask import current_app

class Base_model:
    def set_pwd(self, password: str)->bool:
        '''set password'''
        try:
            self.password = bcrypt.hashpw(password.encode('UTF-8'), bcrypt.gensalt())
            return True
        except:
            current_app.logger.error('An error occured while setting the password', exc_info=True)
            return False
    
    def check_pwd(self, password: str, hashed_pwd: bytes)->bool:
        '''checks if a password is correct'''
        try:
            res = bcrypt.checkpw(password.encode('UTF-8'), hashed_pwd)
        except:
            current_app.logger.error('An error occored while checking the password', exc_info=True)
            return False
        return res
