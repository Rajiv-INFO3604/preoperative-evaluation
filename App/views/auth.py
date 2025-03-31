from flask import Blueprint, render_template, jsonify, request, flash, redirect, url_for
from flask_login import login_user, login_manager, logout_user, LoginManager
from flask_jwt_extended import create_access_token, jwt_required, JWTManager
# from flask_jwt_extended import jwt_required# current_user as jwt_current_user
# from flask_login import login_required, login_user, current_user, logout_user
from App.models import db
from App.controllers import *

auth_views = Blueprint('auth_views', __name__, template_folder='../templates')

'''
Page Routes
'''

@auth_views.route('/signin', methods=['GET'])
def signin_page():
  return render_template('signin.html', title= 'Sign In')

@auth_views.route('/signup', methods=['GET'])
def signup_page():
  return render_template('signup.html', title= 'Sign Up')


'''
Action Routes
'''

@auth_views.route('/signin', methods = ['POST'])
def signin_action():

  data = request.form
  
  patient = Patient.query.filter_by(email = data['email']).first()    
  if patient and patient.check_password(data['password']):
    logout_user()
    login_user(patient)
    return redirect('/patient/profile')
    # return redirect(request.referrer)
  
  anesthesiologist = Anesthesiologist.query.filter_by(email = data['email']).first()
  if anesthesiologist and anesthesiologist.check_password(data['password']):  
    logout_user()
    login_user(anesthesiologist)         
    return redirect('/dashboard/anesthesiologist')
  
  doctor = Doctor.query.filter_by(email = data['email']).first()
  if doctor and doctor.check_password(data['password']):
    logout_user()
    login_user(doctor)
    return redirect('/dashboard/doctor')
    # return redirect('/dashboard/doctor')
  
  flash('Error in email/password.')
  return redirect('/signin')

@auth_views.route('/signup', methods=['POST'])
def signup_action():
  
  try:
    data = request.form     
    print(data)   
    patient = create_patient(firstname=data['firstname'], lastname=data['lastname'], username=data['username'], password = data['password'], email=data['email'], phone_number=data['phone_number'])
    login_user(patient)

    if patient:
      flash('Account Created!')  
      return redirect("/patient/profile") 

  except Exception as e:      
    print("Error in signup: ", e)
    flash("Username, Email, or UWI ID already exist")  # error message
    return redirect(url_for('auth_views.signup_page'))


@auth_views.route('/identify', methods=['GET'])
def identify_page():
    if current_user.is_authenticated:
      return jsonify({'message': f"{current_user.get_json()}"}) 
    return jsonify({'message': "Not Logged In"})

  
@auth_views.route('/logout', methods=['GET'])
def logout_action():
    logout()
    flash('Logged Out!')
    return redirect('/')

'''
API Routes
'''

# @auth_views.route('/api/users', methods=['GET'])
# def get_users_action():
#     users = get_all_users_json()
#     return jsonify(users)

# @auth_views.route('/api/users', methods=['POST'])
# def create_user_endpoint():
#     data = request.json
#     response = create_user(data['username'], data['password'])
#     if response:
#         return jsonify({'message': f"user created"}), 201
#     return jsonify(error='error creating user'), 500

@auth_views.route('/api/signin', methods=['POST'])
def user_login_api():
  data = request.json
  logout_user()
  user_credentials = jwt_authenticate(data['email'], data['password'])

  if not user_credentials:
    return jsonify(error='bad email or password given'), 401

  if 'admin_id' in user_credentials:
    return jsonify(user_credentials)
  else:
    return jsonify(access_token=user_credentials)


# @auth_views.route('/api/identify', methods=['GET'])
# @jwt_required()
# def identify_user_action():
#     return jsonify({'message': f"username: {jwt_current_user.username}, id : {jwt_current_user.id}"})
