from sqlalchemy import Column, Integer, String, Float, DateTime, Date, Enum, ForeignKey, Boolean, Time
from sqlalchemy.orm import relationship, declarative_base

Base = declarative_base()

# Users
class Users(Base):
    __tablename__ = 'users'

    user_id = Column(Integer, unique=True, primary_key=True)
    name = Column(String)
    email = Column(String, unique=True)
    contact = Column(Integer, unique=True)
    birthday = Column(Date)
    gender = Column(Enum('male', 'female', 'trans', 'undisclosed', 'other'))
    password = Column(String)
    reg_date = Column(Date)
    
    # relationships
    prescriptions = relationship('Prescriptions', back_populates='user')
    bookings = relationship('Bookings', back_populates='user')
    payments = relationship('Payments', back_populates='user')

# Hospitals
class Hospitals(Base):
    __tablename__ = 'hospitals'

    hosp_id = Column(Integer, unique=True, primary_key=True)
    hosp_name = Column(String)
    hosp_location = Column(String)
    contact = Column(Integer, unique=True)
    email = Column(String, unique=True)
    
    # relationships
    staff = relationship('Staff', back_populates='hospital')
    pharmacy = relationship('Pharmacy', back_populates='hospital')
    bookings = relationship('Bookings', back_populates='hospital')
    payments = relationship('Payments', back_populates='hospital')
    revenues = relationship('Revenue', back_populates='hospital')

# Staff
class Staff(Base):
    __tablename__ = 'staff'

    staff_id = Column(Integer, unique=True, primary_key=True)
    staff_name = Column(String)
    service = Column(String)
    availability = Column(Boolean)
    
    # fk to hospitals
    hosp_id = Column(Integer, ForeignKey('hospitals.hosp_id'))
    
    # relationships
    bookings = relationship('Bookings', back_populates='staff')
    hospital = relationship('Hospitals', back_populates='staff')

# Pharmacy
class Pharmacy(Base):
    __tablename__ = 'pharmacy'

    pharm_id = Column(Integer, primary_key=True, unique=True)
    name = Column(String)
    location = Column(String)
    contact = Column(Integer, unique=True)
    email = Column(String,  unique=True)
    
    # fk to hospitals
    hosp_id = Column(Integer, ForeignKey('hospitals.hosp_id'), nullable=True)
    
    # relationships
    stock = relationship('Stock', back_populates='pharmacy')
    hospital = relationship('Hospitals', back_populates='pharmacy')
    payments = relationship('Payments', back_populates='pharmacy')
    revenues = relationship('Revenue', back_populates='pharmacy')

# Medicine
class Medicine(Base):
    __tablename__ = 'medicine'

    meds_id = Column(Integer, primary_key=True, unique=True)
    meds_name = Column(String)
    manufacturer = Column(String)
    
    # relationships
    stock = relationship('Stock', back_populates='medicine')

# Junction table for medicine and pharmacy stock
class Stock(Base):
    __tablename__ = 'stock'

    stock_id = Column(Integer, primary_key=True, unique=True)
    price = Column(Float)
    quantity = Column(Float)
    availability = Column(String, nullable=True)
    
    # fk to pharmacy and meds
    pharm_id = Column(Integer, ForeignKey('pharmacy.pharm_id'))
    meds_id = Column(Integer, ForeignKey('medicine.meds_id'))
    
    # relationships
    pharmacy = relationship('Pharmacy', back_populates='stock')
    medicine = relationship('Medicine', back_populates='stock')

# Prescriptions
class Prescriptions(Base):
    __tablename__ = 'prescriptions'

    presc_id = Column(Integer, primary_key=True, unique=True)
    date_issued = Column(DateTime)
    diagnosis = Column(String)
    prescription = Column(String)
    staff_id = Column(Integer)
    hosp_id = Column(Integer)
    fully_filled = Column(Boolean)
    
    # fk to users
    user_id = Column(Integer, ForeignKey('users.user_id'))
    
    # relationships
    user = relationship('Users', back_populates='prescriptions')

# Bookings
class Bookings(Base):
    __tablename__ = 'bookings'

    booking_id = Column(Integer, primary_key=True, unique=True)
    date = Column(DateTime)
    started = Column(Time)
    ended = Column(Time)
    cost = Column(Float)
    complete = Column(Boolean)
    
    # fk
    user_id = Column(Integer, ForeignKey('users.user_id'))
    hosp_id = Column(Integer, ForeignKey('hospitals.hosp_id'))
    staff_id = Column(Integer, ForeignKey('staff.staff_id'))
    
    # relationships
    user = relationship('Users', back_populates='bookings')
    hospital = relationship('Hospitals', back_populates='bookings')
    staff = relationship('Staff', back_populates='bookings')

# Payments
class Payments(Base):
    __tablename__ = 'payments'

    pay_id = Column(Integer, primary_key=True, unique=True)
    bill_type = Column(String)
    amount = Column(Float)
    pay_method = Column(String)
    date = Column(DateTime)
    
    # fk
    user_id = Column(Integer, ForeignKey('users.user_id'))
    pharm_id = Column(Integer, ForeignKey('pharmacy.pharm_id'))
    hosp_id = Column(Integer, ForeignKey('hospitals.hosp_id'))
    
    # relationships
    user = relationship('Users', back_populates='payments')
    pharmacy = relationship('Pharmacy', back_populates='payments')
    hospital = relationship('Hospitals', back_populates='payments')
    revenues = relationship('Revenue', back_populates='payment')

# Revenue
class Revenue(Base):
    __tablename__ = 'revenue'

    pay_id_1 = Column(Integer, ForeignKey('payments.pay_id'), primary_key=True)
    gross_income = Column(Float)
    net_income = Column(Float)
    vd_profit = Column(Float)
    
    # fk
    pharm_id = Column(Integer, ForeignKey('pharmacy.pharm_id'))
    hosp_id = Column(Integer, ForeignKey('hospitals.hosp_id'))
    
    # relationships
    payment = relationship('Payments', back_populates='revenues')
    pharmacy = relationship('Pharmacy', back_populates='revenues')
    hospital = relationship('Hospitals', back_populates='revenues')
