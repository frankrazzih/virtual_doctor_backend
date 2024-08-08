from sqlalchemy import Column, Integer, String, Float, DateTime, Date, Enum, ForeignKey, Boolean, Time
from sqlalchemy.orm import relationship
from flask_sqlalchemy import SQLAlchemy
from .base_model import Base_model

db = SQLAlchemy()

# Patients
class Patients(db.Model, Base_model):
    __tablename__ = 'patients'

    patient_id = db.Column(db.Integer, unique=True, primary_key=True)
    patient_uuid = db.Column(db.String(36), unique=True, nullable=False)
    name = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    contact = db.Column(db.String(30), unique=True, nullable=False)
    birthday = db.Column(db.Date, nullable=False)
    gender = db.Column(db.Enum('male', 'female', 'trans', 'other'))
    password = db.Column(db.String(255), nullable=False)
    reg_date = db.Column(db.DateTime, nullable=False)
    
    # relationships
    prescriptions = relationship('Prescriptions', back_populates='patient')
    bookings = relationship('Bookings', back_populates='patient')
    payments = relationship('Payments', back_populates='patient')
    pharm_orders = relationship('Pharm_orders', back_populates='patient')

# Hospitals
class Hospitals(db.Model, Base_model):
    __tablename__ = 'hospitals'

    hosp_id = db.Column(db.Integer, unique=True, primary_key=True)
    hosp_uuid = db.Column(db.String(36), unique=True, nullable=False)
    hosp_name = db.Column(db.String(255), nullable=False)
    hosp_address = db.Column(db.String(255), nullable=False)
    contact = db.Column(db.String(30), unique=True, nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password = db.Column(db.String(255))
    verification = db.Column(db.Enum('verified', 'unverified'), default='unverified')
    reg_date = db.Column(db.Date, default=None)
    
    # relationships
    doctors = relationship('Doctors', back_populates='hospital')
    pharmacy = relationship('Pharmacy', back_populates='hospital')
    bookings = relationship('Bookings', back_populates='hospital')
    payments = relationship('Payments', back_populates='hospital')
    revenues = relationship('Revenue', back_populates='hospital')
    services = relationship('Services', back_populates='hospital')

class Services(db.Model):
    __tablename__ = 'services'

    service_id = Column(db.Integer, primary_key=True, unique=True)
    service = Column(db.String(255), nullable=False)
    cost = Column(db.Float, nullable=False)

    #fk to hospitals
    hosp_id = Column(db.Integer, db.ForeignKey('hospitals.hosp_id'), nullable=False)
    
    # relationships
    hospital = relationship('Hospitals', back_populates='services')
     #ensure no duplicate entries
    __table_args__ = (
        db.UniqueConstraint('service', 'hosp_id', name='service_hosp_unique'),
    )

# Doctors
class Doctors(db.Model, Base_model):
    __tablename__ = 'doctors'

    doctor_id = db.Column(db.Integer, unique=True, primary_key=True)
    doctor_uuid = db.Column(db.String(36), unique=True)
    doctor_name = db.Column(db.String(255))
    email = db.Column(db.String(255), unique=True)
    contact = db.Column(db.String(30), unique=True)
    service = db.Column(db.String(255))
    availability = db.Column(db.Boolean, default=True)
    password = db.Column(db.String(255))
    
    # fk to hospitals
    hosp_id = db.Column(db.Integer, db.ForeignKey('hospitals.hosp_id'))
    
    # relationships
    bookings = relationship('Bookings', back_populates='doctor')
    hospital = relationship('Hospitals', back_populates='doctors')

# Pharmacy
class Pharmacy(db.Model, Base_model):
    __tablename__ = 'pharmacy'

    pharm_id = db.Column(db.Integer, primary_key=True, unique=True)
    pharm_uuid = db.Column(db.String(36), unique=True)  # Updated to String
    pharm_name = db.Column(db.String(255))
    pharm_address = db.Column(db.String(255))
    contact = db.Column(db.String(30), unique=True)
    email = db.Column(db.String(255), unique=True)
    password = db.Column(db.String(255))
    verification = db.Column(db.Enum('verified', 'unverfied'), default='unverified')
    reg_date = db.Column(db.Date)
    
    # fk to hospitals
    hosp_id = db.Column(db.Integer, db.ForeignKey('hospitals.hosp_id'), nullable=True)
    
    # relationships
    stock = relationship('Stock', back_populates='pharmacy')
    hospital = relationship('Hospitals', back_populates='pharmacy')
    payments = relationship('Payments', back_populates='pharmacy')
    revenues = relationship('Revenue', back_populates='pharmacy')
    pharm_orders = relationship('Pharm_orders', back_populates='pharmacy')

# Medicine
class Medicine(db.Model):
    __tablename__ = 'medicine'

    meds_id = db.Column(db.Integer, primary_key=True, unique=True)
    meds_uuid = db.Column(db.String(36), unique=True)  # Updated to String
    gen_name = db.Column(db.String(255))
    brand_name = db.Column(db.String(255))
    
    # relationships
    stock = relationship('Stock', back_populates='medicine')

# Junction table for medicine and pharmacy stock
class Stock(db.Model):
    __tablename__ = 'stock'

    stock_id = db.Column(db.Integer, primary_key=True, unique=True)
    stock_uuid = db.Column(db.String(36), unique=True)
    price = db.Column(db.Float)
    quant = db.Column(db.Float)
    avail = db.Column(db.Boolean, default=True)
    mfr = db.Column(db.String(255))
    
    # fk to pharmacy and meds
    pharm_id = db.Column(db.Integer, db.ForeignKey('pharmacy.pharm_id'))
    meds_id = db.Column(db.Integer, db.ForeignKey('medicine.meds_id'))
    
    # relationships
    pharmacy = relationship('Pharmacy', back_populates='stock')
    medicine = relationship('Medicine', back_populates='stock')
    #ensure no duplicate entries
    __table_args__ = (
        db.UniqueConstraint('pharm_id', 'meds_id', name='pharm_med_unique'),
    )

# Prescriptions
class Prescriptions(db.Model):
    __tablename__ = 'prescriptions'

    presc_id = db.Column(db.Integer, primary_key=True, unique=True)
    presc_uuid = db.Column(db.String(36), unique=True)  # Updated to String
    date_issued = db.Column(db.DateTime)
    report = db.Column(db.String(2550))
    prescription = db.Column(db.String(2550))
    doctor_id = db.Column(db.Integer)
    hosp_id = db.Column(db.Integer)
    status = db.Column(db.String(25))
    
    # fk to patients
    patient_id = db.Column(db.Integer, db.ForeignKey('patients.patient_id'))
    
    # relationships
    patient = relationship('Patients', back_populates='prescriptions')

class Pharm_orders(db.Model):
    __tablename__ = 'pharm_orders'

    order_id = db.Column(db.Integer, primary_key=True, unique=True)
    order_uuid = db.Column(db.String(36), unique=True)
    presc = db.Column(db.String(2550))
    price = db.Column(db.Float)
    status = db.Column(db.String(36))
    order_date = db.Column(db.DateTime)

    #fk
    patient_id = db.Column(db.Integer, db.ForeignKey('patients.patient_id'))
    pharm_id = db.Column(db.Integer, db.ForeignKey('pharmacy.pharm_id'))
    pay_id = db.Column(db.Integer, db.ForeignKey('payments.pay_id'))

    #relationship
    patient = relationship('Patients', back_populates='pharm_orders')
    pharmacy = relationship('Pharmacy', back_populates='pharm_orders')
    payment = relationship('Payments', back_populates='pharm_orders')

# Bookings
class Bookings(db.Model):
    __tablename__ = 'bookings'

    booking_id = db.Column(db.Integer, primary_key=True, unique=True)
    booking_uuid = db.Column(db.String(36), unique=True)
    service = db.Column(db.String(255))
    date = db.Column(db.DateTime)
    scheduled_time = db.Column(db.Time)
    started = db.Column(db.Time)
    ended = db.Column(db.Time)
    cost = db.Column(db.Float)
    complete = db.Column(db.Boolean, default=False)
    
    # fk
    patient_id = db.Column(db.Integer, db.ForeignKey('patients.patient_id'))
    hosp_id = db.Column(db.Integer, db.ForeignKey('hospitals.hosp_id'))
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctors.doctor_id'))
    
    # relationships
    patient = relationship('Patients', back_populates='bookings')
    hospital = relationship('Hospitals', back_populates='bookings')
    doctor = relationship('Doctors', back_populates='bookings')
    payment = relationship('Payments', back_populates='booking')

# Payments
class Payments(db.Model):
    __tablename__ = 'payments'

    pay_id = db.Column(db.Integer, primary_key=True, unique=True)
    pay_uuid = db.Column(db.String(36), unique=True)  # Updated to String
    pay_for = db.Column(db.Enum('consultation', 'pharmacy_order'))
    amount = db.Column(db.Float)
    pay_method = db.Column(db.String(255))
    date = db.Column(db.DateTime)
    status = db.Column(db.Enum('complete', 'incomplete'), default='incomplete')
    transaction_id = db.Column(db.String(30))
    
    # fk
    patient_id = db.Column(db.Integer, db.ForeignKey('patients.patient_id'))
    pharm_id = db.Column(db.Integer, db.ForeignKey('pharmacy.pharm_id'))
    hosp_id = db.Column(db.Integer, db.ForeignKey('hospitals.hosp_id'))
    booking_id = db.Column(db.Integer, db.ForeignKey('bookings.booking_id'))
    
    # relationships
    patient = relationship('Patients', back_populates='payments')
    pharmacy = relationship('Pharmacy', back_populates='payments')
    hospital = relationship('Hospitals', back_populates='payments')
    revenues = relationship('Revenue', back_populates='payment')
    pharm_orders = relationship('Pharm_orders', back_populates='payment')
    booking = relationship('Bookings', back_populates='payment')

# Revenue
class Revenue(db.Model):
    __tablename__ = 'revenue'

    pay_id_1 = db.Column(db.Integer, db.ForeignKey('payments.pay_id'), primary_key=True)
    rev_uuid = db.Column(db.String(36), unique=True)  # Updated to String
    gross_income = db.Column(db.Float)
    net_income = db.Column(db.Float)
    vd_profit = db.Column(db.Float)

    # fk
    pharm_id = db.Column(db.Integer, db.ForeignKey('pharmacy.pharm_id'))
    hosp_id = db.Column(db.Integer, db.ForeignKey('hospitals.hosp_id'))

    # relationships
    payment = relationship('Payments', back_populates='revenues')
    pharmacy = relationship('Pharmacy', back_populates='revenues')
    hospital = relationship('Hospitals', back_populates='revenues')
