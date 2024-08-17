'''routes for pharmacy operations'''

from flask import (
    current_app,
    session,
    Blueprint, 
    render_template, 
    request,
    jsonify,
    redirect,
    url_for,
    flash)
from flask_mail import Message
from models.models import (
    db,
    Pharmacy,
    Stock,
    Medicine
    )
from ..utils import (
    hash_pwd,
    check_pwd,
    gen_uuid,
    send_email,
    get_cur_time
    )
from sqlalchemy import or_

#create a blueprint
pharmacy_bp = Blueprint('pharmacy', __name__)

#registration endpoint
@pharmacy_bp.route('/register', methods=['POST', 'GET'])
def register():
    if request.method == 'POST':
        #collects the pharmacy registration details and save to the db
        name = request.form['name']
        location = request.form['location']
        email = request.form['email']
        contact = request.form['contact']
        password = request.form['password']
        #hash the password
        hashed_pwd = hash_pwd(password)
        #create a new user
        new_pharm = Pharmacy(
            pharm_name = name,\
            pharm_location = location,\
            email = email,\
            contact = contact,\
            password = hashed_pwd,\
            pharm_uuid = gen_uuid(),\
            reg_date = get_cur_time()
        )

        try:
            db.session.add(new_pharm)
            db.session.commit()
            #send an email to confirm pharmacy registration
            subject = 'Virtual Doctor Pharmacy registration'
            recipients = [email]
            body = 'We are pleased to inform you that your pharmacy is now registered\
            in virtual doctor and can start providing its services.\n\
                To continue, log in to your pharmacy portal and upload the medicine you have in stock and ready for sale.\n\
                    Welcome to virtual doctor.'
            send_email(subject, recipients, body)
            flash('Registration was successful')
            return redirect(url_for('public.sign_in', portal='pharmacy'))
        #errors arising due to unique constraint violation
        except:
            db.session.rollback()
            flash('Number or email already exists!')
            return render_template('/private/pharmacy_portal/pharmacy_sign_up.html')
    else:
        #render the registration page
        return render_template('/private/pharmacy_portal/pharmacy_sign_up.html')

# sign_in endpoint
@pharmacy_bp.route('/sign_in', methods=['POST'])
def sign_in():
    """Checks if the entered password matches the one stored in the database for the pharmacy"""
    email = request.form['email']
    password = request.form['password']
    pharm = db.session.query(Pharmacy).filter_by(email=email).first()
    if not pharm:
        flash('Email does not exist! Please try again.')
        return redirect(url_for('public.sign_in', portal='pharmacy'))
    hashed_pwd = pharm.password
    correct_pwd = check_pwd(password, hashed_pwd)
    if correct_pwd:
        session['pharm_id'] = pharm.pharm_id
        return render_template('/private/pharmacy_portal/pharmacy_home.html')
    else:
        flash('Wrong password! Please try again.')
        return redirect(url_for('public.sign_in', portal='pharmacy'))

#logout
@pharmacy_bp.route('/logout', methods=['GET'])
def logout():
    '''logout a pharmacy'''
    session.clear()
    return redirect(url_for('public.home'))

@pharmacy_bp.route('/meds', methods=['POST'])
def meds():
    '''medicine operations in the pharm portal'''
    if request.method == 'POST':
        counter = 1
        while True:
            #retrieve data from all entries
            gen_name = request.form.get(f'gen_name{counter}')
            brand_name = request.form.get(f'brand_name{counter}')
            mfr  = request.form.get(f'mfr{counter}')
            price = request.form.get(f'price{counter}')
            quant = request.form.get(f'quant{counter}')
            counter += 1
            #check if all entries have beeb recorded
            if not price:
                break
            #check if med exists in meds
            med = db.session.query(Medicine).filter(or_(Medicine.gen_name == gen_name, Medicine.brand_name == brand_name)).first()
            #add to meds table
            if not med:
                new_med = Medicine(
                    gen_name = gen_name,
                    brand_name = brand_name,
                    meds_uuid = gen_uuid()
                )
                try:
                    db.session.add(new_med)
                    db.session.commit()
                except Exception as err:
                    db.session.rollback()
                    current_app.logger.error(err, exc_info=True)
                #get med id
                med_id = db.session.query(Medicine.meds_id).filter(or_(Medicine.gen_name == gen_name, Medicine.brand_name == brand_name)).first()[0]
            else:
                med_id = med.meds_id
            #add to stock table
            new_stock = Stock(
                stock_uuid = gen_uuid(),
                price = price,
                quant = quant,
                mfr = mfr,
                pharm_id = session['pharm_id'],
                meds_id = med_id
            )
            try:
                db.session.add(new_stock)
                db.session.commit()
            except Exception as err:
                db.session.rollback()
                current_app.logger.error(err, exc_info=True)

        flash('Upload was successful')
        return render_template('/private/pharmacy_portal/pharmacy_home.html')

@pharmacy_bp.route('/', methods=['GET'])
def home():
    '''render pharmacy homepage'''
    if 'pharm_id' in session:
        return render_template('/private/pharmacy_portal/pharmacy_home.html')
    else:
        return redirect(url_for('public.sign_in', portal='pharmacy'))

