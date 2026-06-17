from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

db = SQLAlchemy()

class User(UserMixin, db.Model):
    id       = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    role     = db.Column(db.String(20), nullable=False)
    name     = db.Column(db.String(100), nullable=False)

    def set_password(self, p): self.password = generate_password_hash(p)
    def check_password(self, p): return check_password_hash(self.password, p)

class Patient(db.Model):
    id             = db.Column(db.Integer, primary_key=True)
    name           = db.Column(db.String(100), nullable=False)
    room           = db.Column(db.String(20),  nullable=False)
    severity       = db.Column(db.String(20),  nullable=False)
    checkin        = db.Column(db.DateTime, default=datetime.now)
    checkout       = db.Column(db.DateTime, nullable=True)
    last_visit     = db.Column(db.DateTime, default=datetime.now)
    nurse          = db.Column(db.String(100), default='Unassigned')
    doctor         = db.Column(db.String(100), default='Unassigned')
    queue_number   = db.Column(db.Integer, nullable=True)   # queue if no staff free
    nurse_done     = db.Column(db.Boolean, default=False)   # nurse ticked
    reception_done = db.Column(db.Boolean, default=False)   # receptionist ticked
    discharged     = db.Column(db.Boolean, default=False)
    brooch         = db.Column(db.String(20), default='Strong')
    wifi           = db.Column(db.String(20), default='Strong')
    camera         = db.Column(db.String(20), default='Active')

class PatientHistory(db.Model):
    id             = db.Column(db.Integer, primary_key=True)
    patient_name   = db.Column(db.String(100), nullable=False)
    room           = db.Column(db.String(20),  nullable=False)
    severity       = db.Column(db.String(20),  nullable=False)
    doctor         = db.Column(db.String(100), nullable=True)
    nurse          = db.Column(db.String(100), nullable=True)
    checkin        = db.Column(db.DateTime, nullable=True)
    checkout       = db.Column(db.DateTime, nullable=True)
    queue_number   = db.Column(db.Integer,  nullable=True)

class Staff(db.Model):
    id       = db.Column(db.Integer, primary_key=True)
    name     = db.Column(db.String(100), nullable=False)
    role     = db.Column(db.String(20),  nullable=False)
    location = db.Column(db.String(50),  default='Unknown')
    status   = db.Column(db.String(20),  default='Available')
    patient  = db.Column(db.String(100), nullable=True)
    free_in  = db.Column(db.Integer, default=0)
    ble      = db.Column(db.String(20), default='Strong')
    wifi     = db.Column(db.String(20), default='Strong')
    bt       = db.Column(db.String(20), default='Strong')
    camera   = db.Column(db.String(20), default='Active')

class Queue(db.Model):
    id         = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patient.id'), nullable=False)
    position   = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now)

def init_db(app):
    db.init_app(app)
    with app.app_context():
        db.create_all()
        if not User.query.first():
            users = [
                {'username':'admin',       'password':'admin123',  'role':'admin',        'name':'Admin'},
                {'username':'drsmith',     'password':'doctor123', 'role':'doctor',       'name':'Dr. Smith'},
                {'username':'drpatel',     'password':'doctor123', 'role':'doctor',       'name':'Dr. Patel'},
                {'username':'draisha',     'password':'doctor123', 'role':'doctor',       'name':'Dr. Aisha'},
                {'username':'drjames',     'password':'doctor123', 'role':'doctor',       'name':'Dr. James'},
                {'username':'nursepriya',  'password':'nurse123',  'role':'nurse',        'name':'Nurse Priya'},
                {'username':'nurseaisha',  'password':'nurse123',  'role':'nurse',        'name':'Nurse Aisha'},
                {'username':'nurserachel', 'password':'nurse123',  'role':'nurse',        'name':'Nurse Rachel'},
                {'username':'nursesandra', 'password':'nurse123',  'role':'nurse',        'name':'Nurse Sandra'},
                {'username':'nursemeena',  'password':'nurse123',  'role':'nurse',        'name':'Nurse Meena'},
                {'username':'reception',   'password':'recep123',  'role':'receptionist', 'name':'Receptionist'},
            ]
            for u in users:
                user = User(username=u['username'], role=u['role'], name=u['name'])
                user.set_password(u['password'])
                db.session.add(user)

            staff = [
                Staff(name='Dr. Smith',    role='doctor', location='ICU',       status='Available', free_in=0, patient=None),
                Staff(name='Dr. Patel',    role='doctor', location='Room 2',    status='Available', free_in=0, patient=None),
                Staff(name='Dr. Aisha',    role='doctor', location='Corridor',  status='Available', free_in=0, patient=None),
                Staff(name='Dr. James',    role='doctor', location='Ward A',    status='Available', free_in=0, patient=None),
                Staff(name='Nurse Priya',  role='nurse',  location='Ward A',    status='Free', patient=None),
                Staff(name='Nurse Aisha',  role='nurse',  location='ICU',       status='Free', patient=None),
                Staff(name='Nurse Rachel', role='nurse',  location='Room 3',    status='Free', patient=None),
                Staff(name='Nurse Sandra', role='nurse',  location='Ward B',    status='Free', patient=None),
                Staff(name='Nurse Meena',  role='nurse',  location='Reception', status='Free', patient=None),
            ]
            for s in staff:
                db.session.add(s)

            db.session.commit()
            print("✅ Database initialized clean!")
