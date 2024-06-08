'''routes for public pages'''

from flask import Blueprint, render_template, request
#create a blueprint
public_bp = Blueprint('public', __name__)

#renders home page
@public_bp.route('/', methods=['GET'])
def home():
    '''returns the public homepage'''
    return render_template('/public/index.html')

#sign_in endpoint
@public_bp.route('/sign_in', methods=['POST', 'GET'])
def sign_in():
    """checks if the enterd password matches the one 
    stored in the database for the customer
    """
    if request.method == 'POST':
        pass
    else:
        #if method is GET
        return render_template('/public/sign_in.html')

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
