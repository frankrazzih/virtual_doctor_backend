'''routes for user operations'''

from flask import (
    Blueprint, 
    render_template, 
    request,
    jsonify,
    flash)
from flask_mail import Message
from models import (
    db,
    Users,
    )
from .utils import (
    hash_pwd,
    check_pwd,
    gen_uuid,
    create_mail_object,
    get_cur_time
    )

#create a blueprint
user_bp = Blueprint('user', __name__)

#registration endpoint
@user_bp.route('/register', methods=['POST', 'GET'])
def register():
    if request.method == 'POST':
        #collects the user registration details and save to the db
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        email = request.form['email']
        contact = request.form['contact']
        birthday = request.form['birthday']
        gender = request.form['gender']
        password = request.form['password']
        #hash the password
        hashed_pwd = hash_pwd(password)
        #create a new user
        new_user = Users(
            first_name = first_name,\
            last_name = last_name,\
            email = email,\
            contact = contact,\
            birthday = birthday,\
            gender = gender,\
            password = hashed_pwd,\
            user_uuid = gen_uuid(),\
            reg_date = get_cur_time()
        )

        try:
            db.session.add(new_user)
            db.session.commit()
            # #send an email to the user confirming registration
            # mail = create_mail_object()
            # msg = Message('VIRTUAL DOCTOR REGISTRATION', sender='naismart@franksolutions.tech', recipients=[email])
            # msg.body = 'Thank You for registering with us!\nYour health matters to us'
            # mail.send(msg)
            # '''
            # #send an email to the admin informing of a new user
            # users = session.query(Customers).filter_by(email=email).first()
            # msg = Message('New user', sender='naismart@franksolutions.tech', recipients=['francischege602@gmail.com'])
            # msg.body = f'{users.first_name} {users.last_name}\n\n\n'
            # mail.send(msg)
            # '''
            flash('Registration was successful')
            return render_template('/private/user_portal/user_sign_in.html')
        #errors arising due to unique constraint violation
        except:
            db.session.rollback()
            flash('Number or email already exists!')
            return render_template('/public/sign_in.html')
        finally:
            db.session.close()
    else:
        #render the registration page
        return render_template('/private/user_portal/user_sign_up.html')

#sign_in endpoint
@user_bp.route('/sign_in', methods=['POST', 'GET'])
def sign_in():
    """checks if the enterd password matches the one 
    stored in the database for the customer
    """
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        hashed_pwd = db.session.query(Users.password).filter_by(email=email).first()
        if hashed_pwd is not None:
            correct_pwd = check_pwd(password, hashed_pwd[0])
        else:
            flash('Email does not exist!. Please try again.')
            return render_template('/private/user_portal/user_sign_in.html')
        if correct_pwd:
            return jsonify('Signed in successfully as user!')
        else:
            flash('Wrong password!. Please try again.')
            return render_template('/private/user_portal/user_sign_in.html')
    elif request.method == 'GET':
        #if method is GET
        return render_template('/private/user_portal/user_sign_in.html')