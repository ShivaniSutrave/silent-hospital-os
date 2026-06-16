import subprocess
import sys
import os
import pickle
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import accuracy_score
from xgboost import XGBClassifier
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

print("""
╔══════════════════════════════════════════════╗
║         SILENT HOSPITAL OS — MAIN            ║
║   One command. Everything runs.              ║
╚══════════════════════════════════════════════╝
""")

# ── STEP 1: Load Data ────────────────────────────────────
print("=" * 55)
print("STEP 1: Loading Real Hospital Data")
print("=" * 55)
df = pd.read_csv('healthcare/train_data.csv')
df.dropna(inplace=True)
print(f"✅ Loaded {len(df):,} real patient records")
print(f"✅ {df['Department'].nunique()} departments")
print(f"✅ {df['Hospital_code'].nunique()} hospitals")
print(f"✅ Age groups: {sorted(df['Age'].unique())}")

# ── STEP 2: Feature Engineering ──────────────────────────
print("\n" + "=" * 55)
print("STEP 2: Feature Engineering")
print("=" * 55)

features = [
    'Department',
    'Severity of Illness',
    'Type of Admission',
    'Age',
    'Visitors with Patient',
    'Admission_Deposit',
    'Ward_Type',
    'Bed Grade',
    'Available Extra Rooms in Hospital',
    'Hospital_type_code',
    'Hospital_region_code',
    'Ward_Facility_Code'
]

le_dict = {}
df_model = df[features + ['Stay']].copy()

for col in ['Department', 'Severity of Illness',
            'Type of Admission', 'Age', 'Ward_Type',
            'Hospital_type_code', 'Hospital_region_code',
            'Ward_Facility_Code', 'Stay']:
    le = LabelEncoder()
    df_model[col] = le.fit_transform(df_model[col])
    le_dict[col] = le

# Extra engineered features
df_model['deposit_per_visitor'] = (
    df['Admission_Deposit'] /
    (df['Visitors with Patient'] + 1)
)
df_model['rooms_x_severity'] = (
    df_model['Available Extra Rooms in Hospital'] *
    df_model['Severity of Illness']
)
features += ['deposit_per_visitor', 'rooms_x_severity']

X = df_model[features]
y = df_model['Stay']

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42)

print(f"✅ {len(features)} features engineered")
print(f"✅ Training: {len(X_train):,} | Testing: {len(X_test):,}")

# ── STEP 3: Train Best Model ──────────────────────────────
print("\n" + "=" * 55)
print("STEP 3: Training Best Model")
print("=" * 55)

print("\n⏳ Training Random Forest (tuned)...")
rf = RandomForestClassifier(
    n_estimators=500,
    max_depth=25,
    min_samples_split=3,
    min_samples_leaf=1,
    max_features='sqrt',
    random_state=42,
    n_jobs=-1
)
rf.fit(X_train, y_train)
rf_acc = accuracy_score(y_test, rf.predict(X_test))
print(f"✅ Random Forest: {rf_acc * 100:.2f}%")

print("\n⏳ Training XGBoost (tuned)...")
xgb = XGBClassifier(
    n_estimators=700,
    max_depth=12,
    learning_rate=0.03,
    subsample=0.85,
    colsample_bytree=0.85,
    min_child_weight=3,
    gamma=0.1,
    eval_metric='mlogloss',
    random_state=42,
    n_jobs=-1
)
xgb.fit(X_train, y_train)
xgb_acc = accuracy_score(y_test, xgb.predict(X_test))
print(f"✅ XGBoost: {xgb_acc * 100:.2f}%")

best_acc = max(rf_acc, xgb_acc)
best_model = rf if rf_acc > xgb_acc else xgb
best_name = "Random Forest" if rf_acc > xgb_acc else "XGBoost"

print(f"\n🏆 Best Model: {best_name} — {best_acc * 100:.2f}%")
print(f"📈 Improvement from baseline: "
      f"+{(best_acc - 0.2482) * 100:.2f}%")

# ── STEP 4: Save Model ───────────────────────────────────
print("\n" + "=" * 55)
print("STEP 4: Saving Model")
print("=" * 55)
with open('best_model.pkl', 'wb') as f:
    pickle.dump(best_model, f)
with open('label_encoders.pkl', 'wb') as f:
    pickle.dump(le_dict, f)
with open('feature_list.pkl', 'wb') as f:
    pickle.dump(features, f)
print("✅ best_model.pkl saved")
print("✅ label_encoders.pkl saved")
print("✅ feature_list.pkl saved")

# ── STEP 5: Hospital OS Simulation ───────────────────────
print("\n" + "=" * 55)
print("STEP 5: Running Silent Hospital OS")
print("=" * 55)

now = datetime.now()

doctors = [
    {'name': 'Dr. Smith',  'location': 'ICU',      'status': 'Busy',
     'patient': 'P101', 'free_at': now + timedelta(minutes=20)},
    {'name': 'Dr. Patel',  'location': 'Room 2',   'status': 'Available',
     'patient': None,   'free_at': now},
    {'name': 'Dr. Aisha',  'location': 'Corridor', 'status': 'Available',
     'patient': None,   'free_at': now},
    {'name': 'Dr. James',  'location': 'Ward A',   'status': 'Busy',
     'patient': 'P103', 'free_at': now + timedelta(minutes=45)},
]

nurses = [
    {'name': 'Nurse Priya',  'location': 'Ward A',    'status': 'Free',
     'patient': None,   'free_at': now},
    {'name': 'Nurse Aisha',  'location': 'ICU',       'status': 'Busy',
     'patient': 'P101', 'free_at': now + timedelta(minutes=15)},
    {'name': 'Nurse Rachel', 'location': 'Room 3',    'status': 'Free',
     'patient': None,   'free_at': now},
    {'name': 'Nurse Sandra', 'location': 'Ward B',    'status': 'Busy',
     'patient': 'P102', 'free_at': now + timedelta(minutes=30)},
    {'name': 'Nurse Meena',  'location': 'Reception', 'status': 'On Break',
     'patient': None,   'free_at': now + timedelta(minutes=10)},
]

patients = [
    {'id': 'P101', 'name': 'Mr. Ahmed',  'room': 'ICU',
     'severity': 'Extreme',  'wait': 5,
     'nurse': 'Nurse Aisha',  'doctor': 'Dr. Smith'},
    {'id': 'P102', 'name': 'Mrs. Patel', 'room': 'Ward A',
     'severity': 'Moderate', 'wait': 95,
     'nurse': 'Nurse Sandra', 'doctor': None},
    {'id': 'P103', 'name': 'Mr. James',  'room': 'Room 3',
     'severity': 'Minor',    'wait': 20,
     'nurse': None,           'doctor': 'Dr. James'},
    {'id': 'P104', 'name': 'Ms. Sara',   'room': 'Room 1',
     'severity': 'Extreme',  'wait': 130,
     'nurse': None,           'doctor': None},
    {'id': 'P105', 'name': 'Mr. Khan',   'room': 'Ward B',
     'severity': 'Moderate', 'wait': 40,
     'nurse': None,           'doctor': None},
]

beds = [
    {'room': 'ICU',    'status': 'Occupied',
     'free_at': now + timedelta(hours=3)},
    {'room': 'Ward A', 'status': 'Occupied',
     'free_at': now + timedelta(hours=1, minutes=45)},
    {'room': 'Room 3', 'status': 'Occupied',
     'free_at': now + timedelta(minutes=90)},
    {'room': 'Room 1', 'status': 'Occupied',
     'free_at': now + timedelta(hours=5)},
    {'room': 'Ward B', 'status': 'Free',     'free_at': now},
    {'room': 'Room 2', 'status': 'Free',     'free_at': now},
]

# Auto routing
free_nurses = [n for n in nurses if n['status'] == 'Free']
free_doctors = [d for d in doctors if d['status'] == 'Available']

print("\n🔄 AUTO ROUTING:")
for p in patients:
    if p['nurse'] is None and free_nurses:
        nurse = free_nurses.pop(0)
        p['nurse'] = nurse['name']
        nurse['status'] = 'Busy'
        print(f"  ✅ {p['name']} → {nurse['name']} (nurse)")
    if p['doctor'] is None and free_doctors:
        doctor = free_doctors.pop(0)
        p['doctor'] = doctor['name']
        doctor['status'] = 'Busy'
        print(f"  ✅ {p['name']} → {doctor['name']} (doctor)")

print("\n🚨 ALERTS:")
for p in patients:
    if p['wait'] > 60:
        print(f"  ⚠️  {p['name']} waiting {p['wait']} mins "
              f"— {p['severity']} in {p['room']}")

two_hours = now + timedelta(hours=2)
print("\n🛏️  BEDS FREE IN 2 HOURS:")
for b in beds:
    if b['status'] == 'Free':
        print(f"  ✅ {b['room']} — FREE NOW")
    elif b['free_at'] <= two_hours:
        mins = int((b['free_at'] - now).total_seconds() / 60)
        print(f"  🔜 {b['room']} — free in {mins} mins")

# ── STEP 6: Predict a Patient ────────────────────────────
print("\n" + "=" * 55)
print("STEP 6: Live Patient Stay Prediction")
print("=" * 55)

sample = X_test.iloc[0:5]
preds = best_model.predict(sample)
stay_le = le_dict['Stay']
pred_labels = stay_le.inverse_transform(preds)

print("\nSample predictions from real test data:")
print(f"{'#':<4} {'Predicted Stay':<20} {'Actual Stay'}")
print("-" * 45)
actual = stay_le.inverse_transform(y_test.iloc[0:5])
for i, (pred, act) in enumerate(zip(pred_labels, actual)):
    match = "✅" if pred == act else "❌"
    print(f"  {i+1}  {pred:<20} {act}  {match}")

# ── STEP 7: Launch Dashboard ─────────────────────────────
print("\n" + "=" * 55)
print("STEP 7: Launching Dashboard")
print("=" * 55)
print(f"\n✅ Model Accuracy : {best_acc * 100:.2f}%")
print(f"✅ Patients tracked : {len(patients)}")
print(f"✅ Doctors tracked  : {len(doctors)}")
print(f"✅ Nurses tracked   : {len(nurses)}")
print(f"✅ Beds tracked     : {len(beds)}")
print("\n🚀 Launching Silent Hospital OS Dashboard...")
print("   Open Chrome → http://127.0.0.1:8050\n")

os.system("python dashboard.py")