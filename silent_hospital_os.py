import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
import random
import time
from datetime import datetime, timedelta

print("""
╔══════════════════════════════════════════╗
║        SILENT HOSPITAL OS v1.0           ║
║   No interaction. Just works.            ║
╚══════════════════════════════════════════╝
""")

# ── REAL DATA ───────────────────────────────────────────
df = pd.read_csv('healthcare/train_data.csv')
df.dropna(inplace=True)

# ── PART 1: Patient Stay Prediction ─────────────────────
print("=" * 50)
print("MODULE 1: Patient Stay Predictor")
print("=" * 50)

features = ['Department', 'Severity of Illness',
            'Type of Admission', 'Age',
            'Visitors with Patient', 'Admission_Deposit']

le_dict = {}
df_model = df[features + ['Stay']].copy()
for col in ['Department', 'Severity of Illness',
            'Type of Admission', 'Age', 'Stay']:
    le = LabelEncoder()
    df_model[col] = le.fit_transform(df_model[col])
    le_dict[col] = le

X = df_model[features]
y = df_model['Stay']
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42)

model = RandomForestClassifier(
    n_estimators=100, random_state=42, n_jobs=-1)
model.fit(X_train, y_train)
accuracy = model.score(X_test, y_test)
print(f"\n✅ Model trained on {len(X_train):,} real patients")
print(f"✅ Accuracy: {accuracy * 100:.2f}%")

# ── HOSPITAL PEOPLE DATA ─────────────────────────────────
now = datetime.now()

doctors = [
    {'id': 'D001', 'name': 'Dr. Smith',   'badge_location': 'ICU',
     'status': 'Busy',      'current_patient': 'P101', 'free_at': now + timedelta(minutes=20)},
    {'id': 'D002', 'name': 'Dr. Patel',   'badge_location': 'Room 2',
     'status': 'Available', 'current_patient': None,   'free_at': now},
    {'id': 'D003', 'name': 'Dr. Aisha',   'badge_location': 'Corridor',
     'status': 'Available', 'current_patient': None,   'free_at': now},
    {'id': 'D004', 'name': 'Dr. James',   'badge_location': 'Ward A',
     'status': 'Busy',      'current_patient': 'P103', 'free_at': now + timedelta(minutes=45)},
]

nurses = [
    {'id': 'N001', 'name': 'Nurse Priya',  'badge_location': 'Ward A',
     'status': 'Free',     'current_patient': None,   'free_at': now},
    {'id': 'N002', 'name': 'Nurse Aisha',  'badge_location': 'ICU',
     'status': 'Busy',     'current_patient': 'P101', 'free_at': now + timedelta(minutes=15)},
    {'id': 'N003', 'name': 'Nurse Rachel', 'badge_location': 'Room 3',
     'status': 'Free',     'current_patient': None,   'free_at': now},
    {'id': 'N004', 'name': 'Nurse Sandra', 'badge_location': 'Ward B',
     'status': 'Busy',     'current_patient': 'P102', 'free_at': now + timedelta(minutes=30)},
    {'id': 'N005', 'name': 'Nurse Meena',  'badge_location': 'Reception',
     'status': 'On Break', 'current_patient': None,   'free_at': now + timedelta(minutes=10)},
]

patients = [
    {'id': 'P101', 'name': 'Mr. Ahmed',   'room': 'ICU',
     'severity': 'Extreme',  'waiting_since': now - timedelta(minutes=5),
     'wristband': 'active',  'assigned_nurse': 'N002', 'assigned_doctor': 'D001'},
    {'id': 'P102', 'name': 'Mrs. Patel',  'room': 'Ward A',
     'severity': 'Moderate', 'waiting_since': now - timedelta(minutes=95),
     'wristband': 'active',  'assigned_nurse': 'N004', 'assigned_doctor': None},
    {'id': 'P103', 'name': 'Mr. James',   'room': 'Room 3',
     'severity': 'Minor',    'waiting_since': now - timedelta(minutes=20),
     'wristband': 'active',  'assigned_nurse': None,   'assigned_doctor': 'D004'},
    {'id': 'P104', 'name': 'Ms. Sara',    'room': 'Room 1',
     'severity': 'Extreme',  'waiting_since': now - timedelta(minutes=130),
     'wristband': 'active',  'assigned_nurse': None,   'assigned_doctor': None},
    {'id': 'P105', 'name': 'Mr. Khan',    'room': 'Ward B',
     'severity': 'Moderate', 'waiting_since': now - timedelta(minutes=40),
     'wristband': 'active',  'assigned_nurse': None,   'assigned_doctor': None},
]

beds = [
    {'id': 'B001', 'room': 'ICU',       'status': 'Occupied', 'patient': 'P101', 'free_at': now + timedelta(hours=3)},
    {'id': 'B002', 'room': 'Ward A',    'status': 'Occupied', 'patient': 'P102', 'free_at': now + timedelta(hours=1, minutes=45)},
    {'id': 'B003', 'room': 'Room 3',    'status': 'Occupied', 'patient': 'P103', 'free_at': now + timedelta(minutes=90)},
    {'id': 'B004', 'room': 'Room 1',    'status': 'Occupied', 'patient': 'P104', 'free_at': now + timedelta(hours=5)},
    {'id': 'B005', 'room': 'Ward B',    'status': 'Free',     'patient': None,   'free_at': now},
    {'id': 'B006', 'room': 'Room 2',    'status': 'Free',     'patient': None,   'free_at': now},
]

receptionist = {
    'name': 'Reception Desk',
    'computer': 'online',
    'pending_queries': ['Family of P102 waiting for update',
                        'Family of P104 asking about discharge']
}

# ── MODULE 2: DOCTOR AVAILABILITY ────────────────────────
print("\n" + "=" * 50)
print("MODULE 2: Doctor Availability & Location")
print("=" * 50)
print(f"\n{'Name':<16} {'Location':<12} {'Status':<12} {'Free At'}")
print("-" * 55)
for d in doctors:
    free_time = d['free_at'].strftime('%I:%M %p') if d['status'] == 'Busy' else 'NOW'
    print(f"  {d['name']:<14} {d['badge_location']:<12} {d['status']:<12} {free_time}")

# ── MODULE 3: NURSE ASSIGNMENT ───────────────────────────
print("\n" + "=" * 50)
print("MODULE 3: Nurse Status & Auto Assignment")
print("=" * 50)
print(f"\n{'Name':<16} {'Location':<12} {'Status':<12} {'Handling'}")
print("-" * 55)
for n in nurses:
    handling = n['current_patient'] if n['current_patient'] else '—'
    print(f"  {n['name']:<14} {n['badge_location']:<12} {n['status']:<12} {handling}")

free_nurses = [n for n in nurses if n['status'] == 'Free']
unassigned_patients = [p for p in patients if p['assigned_nurse'] is None]

print(f"\n🔄 AUTO ROUTING — {len(unassigned_patients)} patients need a nurse:")
print("-" * 55)
for p in unassigned_patients:
    if free_nurses:
        nurse = free_nurses.pop(0)
        nurse['status'] = 'Busy'
        nurse['current_patient'] = p['id']
        p['assigned_nurse'] = nurse['id']
        print(f"  ✅ {p['name']:<14} ({p['room']}) → {nurse['name']}")
    else:
        soonest = min(nurses, key=lambda n: n['free_at'])
        mins = int((soonest['free_at'] - now).total_seconds() / 60)
        print(f"  ⏳ {p['name']:<14} ({p['room']}) → {soonest['name']} free in {mins} mins")

# ── MODULE 4: PATIENTS WAITING TOO LONG ──────────────────
print("\n" + "=" * 50)
print("MODULE 4: Patients Waiting Too Long")
print("=" * 50)
WAIT_THRESHOLD = 60
print(f"\n⚠️  Flagging patients waiting over {WAIT_THRESHOLD} minutes:\n")
flagged = False
for p in patients:
    wait = int((now - p['waiting_since']).total_seconds() / 60)
    if wait > WAIT_THRESHOLD:
        flagged = True
        doc = next((d['name'] for d in doctors
                    if d['id'] == p.get('assigned_doctor')), 'Unassigned')
        print(f"  🚨 {p['name']:<14} | Room: {p['room']:<10} | "
              f"Severity: {p['severity']:<10} | Waited: {wait} mins")
        print(f"     Doctor: {doc}")
        print()
if not flagged:
    print("  ✅ No patients waiting too long right now.")

# ── MODULE 5: BED AVAILABILITY ───────────────────────────
print("=" * 50)
print("MODULE 5: Bed Management — Free in 2 Hours")
print("=" * 50)
two_hours = now + timedelta(hours=2)
print(f"\n🛏️  Beds freeing up before {two_hours.strftime('%I:%M %p')}:\n")
found = False
for b in beds:
    if b['status'] == 'Free':
        print(f"  ✅ {b['room']:<12} | Already FREE now")
        found = True
    elif b['free_at'] <= two_hours:
        mins = int((b['free_at'] - now).total_seconds() / 60)
        print(f"  🔜 {b['room']:<12} | Free in {mins} mins "
              f"(patient {b['patient']} discharging)")
        found = True
if not found:
    print("  ⚠️  No beds freeing up in next 2 hours.")

# ── MODULE 6: RECEPTIONIST DASHBOARD ─────────────────────
print("\n" + "=" * 50)
print("MODULE 6: Receptionist Auto-Updates")
print("=" * 50)
print(f"\n💻 {receptionist['name']} — System: {receptionist['computer'].upper()}\n")
for query in receptionist['pending_queries']:
    pid = query.split('P')[1][:3]
    patient = next((p for p in patients if p['id'] == f'P{pid}'), None)
    if patient:
        wait = int((now - patient['waiting_since']).total_seconds() / 60)
        nurse_name = next((n['name'] for n in nurses
                          if n['id'] == patient.get('assigned_nurse')), 'Being assigned')
        print(f"  📋 Query: {query}")
        print(f"     → Patient in {patient['room']} | "
              f"Waited: {wait} mins | Nurse: {nurse_name}")
        print()

print("=" * 50)
print("✅ SILENT HOSPITAL OS — All modules running.")
print("   Zero interactions needed. System just works.")
print("=" * 50)