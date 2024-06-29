'''routes for public pages'''

from flask import (
    Blueprint, 
    render_template, 
    request, 
    url_for,
    flash)
from werkzeug.security import (generate_password_hash, 
                               check_password_hash)
#create public blueprint
public_bp = Blueprint('public', __name__)

#renders home page
@public_bp.route('/', methods=['GET'])
def home():
    '''returns the public homepage'''
    return render_template('/public/index.html')

#sign_in endpoint
@public_bp.route('/sign_in', methods=['GET'])
def sign_in():
    """
    check the portal requested to sign in
    """
    portal = request.args.get('portal')
    if not portal:
        return render_template('/public/select_portal.html')
    if portal == 'staff':
        return render_template('/public/sign_in.html', 
                        sign_in=url_for(f'{portal}.sign_in')) 
    return render_template('/public/sign_in.html', 
                        sign_in=url_for(f'{portal}.sign_in'),
                        register=url_for(f'{portal}.register'))


#renders services page
@public_bp.route('/services', methods=['GET'])
def services():
    '''returns the services page'''
    return render_template('/public/services.html')

#renders staff page
@public_bp.route('/staff', methods=['GET'])
def staff():
    '''returns the staff page'''
    return render_template('/public/staff.html')

#renders forums page
@public_bp.route('/forums', methods=['GET'])
def forums():
    '''returns the forums page'''
    return render_template('/public/forums.html')

#renders gallery page
@public_bp.route('/gallery', methods=['GET'])
def gallery():
    '''returns the gallery page'''
    return render_template('/public/gallery.html')

#renders about page
@public_bp.route('/about', methods=['GET'])
def about():
    '''returns the about page'''
    return render_template('/public/about.html')

#renders contact page
@public_bp.route('/contact', methods=['GET'])
def contact():
    '''returns the contact page'''
    return render_template('/public/contact.html')

#renders help page
@public_bp.route('/help', methods=['GET'])
def help():
    '''returns the help page'''
    return render_template('/public/help.html')

#password reset
@public_bp.route('/pwd_reset', methods=['POST', 'GET'])
def pwd_reset():
    if request.method == 'GET':
        return render_template('/public/pwd_reset.html')
    else:
        #POST. check if the email exists
        email = request.form['email']
        check_mail = session.query(Customers.email).filter_by(email=email).first()
        #mail exists
        if check_mail:
            #store the code in the user's session
            code = random.randint(111111, 999999)
            flask_session['code'] = code
            flask_session['email'] = email
            msg = Message('HOSPITAL X RESET PASSWORD', sender='naismart@franksolutions.tech',\
                                                    recipients=[email])
            msg.body = f'Use this code to reset your password\n\n {code}'
            mail.send(msg)
            flash('Enter the code to reset your password')
            return render_template('/public/new_pwd.html')
        #mail does not exist
        else:
            flash('The email does not exist!')
            return redirect(url_for('pwd_reset'))

#create a new password
@public_bp.route('/new_pwd', methods=['POST'])
def new_pwd():
    #verify the code
    if flask_session.get('code') == int(request.form['code']):
        #update password
        password = request.form['new_pwd']
        #hash password
        hashed_pwd = generate_password_hash(password)
        user = session.query(Customers).filter_by(email=flask_session.get('email')).first()
        user.password = hashed_pwd
        #commit the changes
        session.commit()
        session.close()
        flash('Your password has been updated')
        
        #clear the code from the session
        flask_session.pop('code', None)
        return render_template('/public/sign_in.html')
    else:
        flash('Wrong code! Please try again!')
        return render_template('/public/new_pwd.html')

