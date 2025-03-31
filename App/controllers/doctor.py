from App.models import Doctor
from App.database import db
from App.controllers.notification import create_notification
from flask import current_app
from App.extensions import mail
from flask_mail import Message
from App.models.patient import Patient

def create_doctor(firstname, lastname, username, password, email, phone_number):
    try:
        new_doctor = Doctor(firstname=firstname, lastname=lastname, username=username, password=password, email=email, phone_number=phone_number)
        db.session.add(new_doctor)
        db.session.commit()
        return new_doctor
    except Exception as e:
        print(e, "Error creating doctor")
        return None
    

def update_questionnaire_doctor(doctor_id, questionnaire_id, new_doctor_notes, new_operation_date):
    doctor = Doctor.query.get(doctor_id)
    if doctor:
        # Update the questionnaire (this method is defined on the Doctor model)
        questionnaire = doctor.update_questionnaire_doctor(questionnaire_id, new_doctor_notes, new_operation_date)
        if questionnaire:
            # Existing notification creation (if needed)
            notification = create_notification(
                questionnaire.patient_id, 
                f"Doctor {doctor.lastname} has reviewed your questionnaire",
                "Questionnaire Updated"
            )
            
            # Retrieve the patient details using the questionnaire's patient_id
            patient = Patient.query.get(questionnaire.patient_id)
            if patient:
                msg = Message(
                    subject="Surgery Date Scheduled",
                    sender=current_app.config['MAIL_USERNAME'],
                    recipients=[patient.email]
                )
                msg.body = (
                    f"Dear {patient.firstname},\n\n"
                    f"Your surgery is scheduled on {new_operation_date}.\n\n"
                    f"Regards,\nDr. {doctor.lastname}"
                )
                mail.send(msg)
            return True
        else:
            return False
    else:
        return False