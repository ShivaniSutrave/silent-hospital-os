import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier, VotingClassifier, GradientBoostingClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import accuracy_score
from xgboost import XGBClassifier
import warnings
warnings.filterwarnings('ignore')

print("=" * 50)
print("ENSEMBLE MODEL — Pushing Accuracy to 50%+")
print("=" * 50)

print("\n⏳ Loading real hospital data...")
df = pd.read_csv('healthcare/train_data.csv')
df.dropna(inplace=True)

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

X = df_model[features]
y = df_model['Stay']

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42)

print(f"✅ Data ready — {len(X_train):,} training samples\n")

# ── Model 1: Random Forest ───────────────────────────────
print("⏳ Training Random Forest...")
rf = RandomForestClassifier(
    n_estimators=300,
    max_depth=20,
    min_samples_split=5,
    random_state=42,
    n_jobs=-1
)
rf.fit(X_train, y_train)
rf_acc = accuracy_score(y_test, rf.predict(X_test))
print(f"✅ Random Forest: {rf_acc * 100:.2f}%")

# ── Model 2: XGBoost ─────────────────────────────────────
print("\n⏳ Training XGBoost...")
xgb = XGBClassifier(
    n_estimators=500,
    max_depth=10,
    learning_rate=0.05,
    subsample=0.8,
    colsample_bytree=0.8,
    eval_metric='mlogloss',
    random_state=42,
    n_jobs=-1
)
xgb.fit(X_train, y_train)
xgb_acc = accuracy_score(y_test, xgb.predict(X_test))
print(f"✅ XGBoost: {xgb_acc * 100:.2f}%")

# ── Model 3: Ensemble (Both Combined) ───────────────────
print("\n⏳ Training Ensemble (RF + XGBoost combined)...")
ensemble = VotingClassifier(
    estimators=[
        ('rf', rf),
        ('xgb', xgb)
    ],
    voting='soft',
    n_jobs=-1
)
ensemble.fit(X_train, y_train)
ens_acc = accuracy_score(y_test, ensemble.predict(X_test))
print(f"✅ Ensemble: {ens_acc * 100:.2f}%")

# ── Final Results ────────────────────────────────────────
print("\n" + "=" * 50)
print("FINAL RESULTS")
print("=" * 50)
print(f"\n  Previous best : 24.82%  (baseline)")
print(f"  Random Forest : {rf_acc * 100:.2f}%")
print(f"  XGBoost       : {xgb_acc * 100:.2f}%")
print(f"  Ensemble      : {ens_acc * 100:.2f}%  ← BEST")

best = max(rf_acc, xgb_acc, ens_acc)
improvement = (best - 0.2482) * 100
print(f"\n🏆 Total improvement from baseline: +{improvement:.2f}%")

# ── Save the best model ──────────────────────────────────
import pickle
print("\n⏳ Saving best model...")
with open('best_model.pkl', 'wb') as f:
    pickle.dump(ensemble, f)
with open('label_encoders.pkl', 'wb') as f:
    pickle.dump(le_dict, f)
print("✅ Model saved as best_model.pkl")
print("✅ Encoders saved as label_encoders.pkl")
print("\n🚀 Ready for Dashboard and Hospital OS integration!")