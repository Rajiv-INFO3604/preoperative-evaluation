from App.database import db

class Evaluation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patient.id'), nullable=False)
    status = db.Column(db.String(50), nullable=False, default='pending')
    operation_date = db.Column(db.String(50), nullable=True)

    def __init__(self, patient_id, status="pending", operation_date=None):
        self.patient_id = patient_id
        self.status = status
        self.operation_date = operation_date
