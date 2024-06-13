'''routes for pharmacy pages'''

from flask import (
    Blueprint, 
    render_template, 
    request, 
    session as flask_session, 
    flash)
from werkzeug.security import (generate_password_hash, 
                               check_password_hash)
#create a blueprint
pharmacy_bp = Blueprint('pharmacy', __name__)

#registration endpoint
@pharmacy_bp.route('/register', methods=['POST', 'GET'])
def register():
    if request.method == 'POST':
        #collects the user registration details and save the to the db
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        email = request.form['email']
        phone_no = request.form['phone_no']
        password = request.form['password']
        #hash the password
        hashed_pwd = generate_password_hash(password)
        #create a new customer
        newcust = Customers(
            first_name = first_name,\
            last_name = last_name,\
            email = email,\
            phone_no = phone_no,\
            password = hashed_pwd,\
            cust_id = gen_cust_id()
        )

        try:
            session.add(newcust)
            session.commit()
            #send an email to the user confirming registration
            msg = Message('HOSPITAL X REGISTRATION', sender='naismart@franksolutions.tech', recipients=[email])
            msg.body = 'Thank You for registering with HOSPITAL X!'
            mail.send(msg)
            '''
            #send an email to the admin informing of a new user
            users = session.query(Customers).filter_by(email=email).first()
            msg = Message('New user', sender='naismart@franksolutions.tech', recipients=['francischege602@gmail.com'])
            msg.body = f'{users.first_name} {users.last_name}\n\n\n'
            mail.send(msg)
            '''
            print('Email sent successfully!')
            flash('Registration was successful')
            return render_template('/public/sign_in.html')
        #errors arising due to unique constraint violation
        except IntegrityError:
            session.rollback
            flash('Number or email already exists!')
            return render_template('/public/sign_in.html')
        #other errors
        except:
            session.rollback()
            flash('An error occured. Please try again!')
            return render_template('/public/sign_up.html')
        finally:
            session.close()
    else:
        #render the registration page
        return render_template('/private/pharmacy_portal/pharmacy_sign_up.html')

#sign_in endpoint
@pharmacy_bp.route('/sign_in', methods=['POST', 'GET'])
def sign_in():
    """checks if the enterd password matches the one 
    stored in the database for the customer
    """
    if request.method == 'POST':
        pass
    elif request.method == 'GET':
        #if method is GET
        print('USER PORTAL!!')
        return render_template('/private/pharmacy_portal/pharmacy_sign_in.html')