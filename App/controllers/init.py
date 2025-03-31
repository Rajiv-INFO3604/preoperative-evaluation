from App.models import db
from App.controllers.patient import create_patient
from App.controllers.doctor import create_doctor
from App.controllers.anesthesiologist import create_anesthesiologist



def initialize_db():
    db.drop_all()
    db.create_all()   

    patient = create_patient(firstname='John', lastname='Doe', username='johndoe', password='password',phone_number='1234567890',email='johndoe@mail.com')
    doctor = create_doctor(firstname='Jane', lastname='Doe', username='janedoe', password='password',phone_number='0987654321', email='janedoe@mail.com') 
    anesthesiologist = create_anesthesiologist(firstname='Mike', lastname='Smith', username='johnsmith', password='password',phone_number='1234567890', email='mikesmith@mail.com')  
    print('database initialized!')