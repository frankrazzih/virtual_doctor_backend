#validate data
from marshmallow import Schema, fields, ValidationError
from marshmallow.validate import Length
from typing import Dict
from datetime import datetime

class validate_reg_data(Schema):
    '''validates registration data'''
    name = fields.Str(required=True, validate=Length(min=2, max=50))
    email = fields.Email(required=True)
    contact = fields.Str(required=True, validate=Length(min=10, max=15))
    role = fields.Str(required=True, validate= lambda x : x in ['patient', 'hospital', 'pharmacy'])
    #fields specific to patients
    birthday = fields.Date(required=False, validate= lambda date: datetime.now().date() > date)
    gender = fields.Str(required=False, validate= lambda gender : gender in ['male', 'female', 'trans', 'other'])
    pwd = fields.Str(required=False, validate=Length(min=6, max=16))
    #fields specific to others
    file = fields.Str(required=False)
    address = fields.Str(required=False)
    
    #check specific fields
    @validates_schema
    def validate_role_specific_fields(self, data, **kwargs):
        '''validate fields according to roles'''
        role = data.get('role')
        #validate patient fields
        if role == 'patient':
            if not (field for field in data for field in ['birthday', 'gender', 'pwd']):
                raise ValidationError('birthday/gender/pwd missing')
        else:
            if not (field for field in data for field in ['file', 'address']):
                raise ValidationError('file/address missing')

        
    


