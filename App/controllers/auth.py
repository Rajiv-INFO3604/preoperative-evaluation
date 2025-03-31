from flask_login import login_user, login_manager, logout_user, LoginManager, current_user
from flask_jwt_extended import create_access_token, jwt_required, JWTManager, get_jwt_identity, verify_jwt_in_request
from flask import render_template, request, flash, redirect, url_for, current_app
from App.models.patient import Patient
from App.database import db
from App.token import generate_reset_token, verify_reset_token
from App.extensions import mail
from flask_mail import Message
from App.models import User, Doctor, Anesthesiologist, Patient

from functools import wraps

from flask import Blueprint
auth_blueprint = Blueprint('auth', __name__)


def jwt_authenticate(username, password):
    user = Patient.query.filter_by(username=username).first()
  
    if user and user.check_password(password):
        return create_access_token(identity=username)
    
    user = Doctor.query.filter_by(username=username).first()
  
    if user and user.check_password(password):
        return create_access_token(identity=username)

    user = Anesthesiologist.query.filter_by(username=username).first()
  
    if user and user.check_password(password):
        return create_access_token(identity=username)

    return None

def login(username, password):
    user = Patient.query.filter_by(username=username).first()
  
    if user and user.check_password(password):
        return create_access_token(identity=username)

    user = Doctor.query.filter_by(username=username).first()
  
    if user and user.check_password(password):
        return create_access_token(identity=username)

    user = Anesthesiologist.query.filter_by(username=username).first()
  
    if user and user.check_password(password):
        return create_access_token(identity=username)
    return None

def setup_flask_login(app):
    login_manager = LoginManager()
    login_manager.init_app(app)
    
    @login_manager.user_loader
    def load_user(user_id):
        user = Doctor.query.get(user_id)

        if user:
            return user
        
        user = Anesthesiologist.query.get(user_id)

        if user:
            return user

        return Patient.query.get(user_id)
    
    return login_manager

def setup_jwt(app):
    jwt = JWTManager(app)

    @jwt.user_identity_loader
    def user_identity_lookup(identity):

        user = Doctor.query.filter_by(username=identity).one_or_none()
        if user:
            return user.id

        user = Anesthesiologist.query.filter_by(username=identity).one_or_none()
        if user:
            return user.id

        user = Patient.query.filter_by(username=identity).one_or_none()
        if user:
            return user.id
        return None

    @jwt.user_lookup_loader
    def user_lookup_callback(_jwt_header, jwt_data):
        identity = jwt_data["sub"]
        return Patient.query.get(identity)

    return jwt

    #Edits below

#Login actions
def login_anesthesiologist(username, password):
    manager = Anesthesiologist.query.filter_by(username = username).first()

    if manager and manager.check_password(password):
        login_user(manager)
        return manager
    return None   

def login_doctor(username, password):
    doctor = Doctor.query.filter_by(username = username).first()

    if doctor and doctor.check_password(password):
        login_user(doctor)
        return doctor
    return None

def login_patient(name,password):
    patient = Patient.query.filter_by(username = name).first()

    if patient and patient.check_password(password):
        login_user(patient)
        return patient
    return None

#Logout action
def logout():
    logout_user()

#Wrappers
def anesthesiologist_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if not current_user.is_authenticated or not isinstance(current_user, Anesthesiologist):
            return render_template("unauthorized.html"), 401
        return func(*args, **kwargs)
    return wrapper

def doctor_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if not current_user.is_authenticated or not isinstance(current_user, Doctor):
            return render_template("unauthorized.html"), 401
        return func(*args, **kwargs)
    return wrapper

def patient_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):        
        if not  current_user.is_authenticated or not isinstance(current_user, Patient):
            return render_template("unauthorized.html"), 401
        return func(*args, **kwargs)
    return wrapper

# Context processor to make 'is_authenticated' available to all templates
def add_auth_context(app):
  @app.context_processor
  def inject_user():
      try:
          verify_jwt_in_request()
          user_id = get_jwt_identity()
          current_user = User.query.get(user_id)
          is_authenticated = True
      except Exception as e:
          print(e)
          is_authenticated = False
          current_user = None
      return dict(is_authenticated=is_authenticated, current_user=current_user)

@auth_blueprint.route('/reset_password', methods=['GET', 'POST'])
def reset_password_request():
    if request.method == 'POST':
        email = request.form.get('email')
        patient = Patient.query.filter_by(email=email).first()
        if patient:
            token = generate_reset_token(email)
            reset_link = url_for('auth.reset_with_token', token=token, _external=True)
            msg = Message(
                subject="Password Reset Request",
                sender=current_app.config['MAIL_USERNAME'],
                recipients=[email]
            )
            msg.body = (
                f"Dear {patient.firstname},\n\n"
                f"To reset your password, click the following link:\n{reset_link}\n\n"
                f"If you did not request a password reset, please ignore this email.\n\n"
                f"Regards,\nMedCareTT Team"
            )
            mail.send(msg)
            flash('A password reset link has been sent to your email.', 'info')
            return redirect(url_for('auth.sign_in'))
        else:
            flash('Email address not found. Please try again.', 'danger')
    return render_template('reset_password.html', title='Patient Reset Password')

# --- Route to reset the password using the token ---
@auth_blueprint.route('/reset/<token>', methods=['GET', 'POST'])
def reset_with_token(token):
    email = verify_reset_token(token)
    if not email:
        flash('The reset link is invalid or has expired.', 'danger')
        return redirect(url_for('auth.reset_password_request'))
    
    if request.method == 'POST':
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        if password != confirm_password:
            flash('Passwords do not match. Please try again.', 'danger')
            return render_template('new_password.html', token=token)
        
        patient = Patient.query.filter_by(email=email).first()
        if patient:
            patient.set_password(password)
            db.session.commit()
            flash('Your password has been updated successfully.', 'success')
            return redirect(url_for('auth.sign_in'))
        else:
            flash('User not found.', 'danger')
            return redirect(url_for('auth.reset_password_request'))
    
    return render_template('new_password.html', token=token, title= 'Patient New Password')

@auth_blueprint.route('/signin', methods=['GET', 'POST'], endpoint='sign_in')
def sign_in():
    return render_template('signin.html')
