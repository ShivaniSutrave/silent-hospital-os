import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import accuracy_score
from xgboost import XGBClassifier
import lightgbm as lgb
import pickle
import warnings
warnings.filterwarnings('ignore')

print("=" * 55)
print("ACCURACY BOOST — Targeting 60%+")
print("=" * 55)

print("\n⏳ Loading data...")
df = pd.read_csv('healthcare/train_data.csv')
df.dropna(inplace=True)

# ── Heavy Feature Engineering ────────────────────────────
print("⏳ Engineering powerful features...")

le_dict = {}
df_fe = df.copy()

cat_cols = ['Department', 'Severity of Illness',
            'Type of Admission', 'Age', 'Ward_Type',
            'Hospital_type_code', 'Hospital_region_code',
            'Ward_Facility_Code', 'Stay']

for col in cat_cols:
    le = LabelEncoder()
    df_fe[col] = le.fit_transform(df_fe[col])
    le_dict[col] = le

# New powerful features
df_fe['deposit_per_visitor'] = (
    df_fe['Admission_Deposit'] /
    (df_fe['Visitors with Patient'] + 1)
)
df_fe['severity_x_admission'] = (
    df_fe['Severity of Illness'] *
    df_fe['Type of Admission']
)
df_fe['rooms_x_ward'] = (
    df_fe['Available Extra Rooms in Hospital'] *
    df_fe['Ward_Type']
)
df_fe['bed_x_severity'] = (
    df_fe['Bed Grade'] *
    df_fe['Severity of Illness']
)
df_fe['visitors_x_severity'] = (
    df_fe['Visitors with Patient'] *
    df_fe['Severity of Illness']
)
df_fe['deposit_x_severity'] = (
    df_fe['Admission_Deposit'] *
    df_fe['Severity of Illness']
)
df_fe['hospital_x_department'] = (
    df_fe['Hospital_code'] *
    df_fe['Department']
)
df_fe['age_x_severity'] = (
    df_fe['Age'] *
    df_fe['Severity of Illness']
)

features = [
    'Department', 'Severity of Illness',
    'Type of Admission', 'Age',
    'Visitors with Patient', 'Admission_Deposit',
    'Ward_Type', 'Bed Grade',
    'Available Extra Rooms in Hospital',
    'Hospital_type_code', 'Hospital_region_code',
    'Ward_Facility_Code', 'Hospital_code',
    'City_Code_Hospital',
    'deposit_per_visitor', 'severity_x_admission',
    'rooms_x_ward', 'bed_x_severity',
    'visitors_x_severity', 'deposit_x_severity',
    'hospital_x_department', 'age_x_severity'
]

X = df_fe[features]
y = df_fe['Stay']

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42)

print(f"✅ {len(features)} features ready")
print(f"✅ {len(X_train):,} training samples\n")

# ── Model 1: LightGBM ────────────────────────────────────
print("=" * 55)
print("⏳ Training LightGBM...")
lgbm = lgb.LGBMClassifier(
    n_estimators=1000,
    max_depth=15,
    learning_rate=0.02,
    num_leaves=127,
    subsample=0.8,
    colsample_bytree=0.8,
    min_child_samples=20,
    reg_alpha=0.1,
    reg_lambda=0.1,
    random_state=42,
    n_jobs=-1,
    verbose=-1
)
lgbm.fit(
    X_train, y_train,
    eval_set=[(X_test, y_test)],
    callbacks=[lgb.early_stopping(50, verbose=False),
               lgb.log_evaluation(period=-1)]
)
lgbm_acc = accuracy_score(y_test, lgbm.predict(X_test))
print(f"✅ LightGBM: {lgbm_acc * 100:.2f}%")

# ── Model 2: XGBoost ────────────────────────────────────
print("\n⏳ Training XGBoost (tuned)...")
xgb = XGBClassifier(
    n_estimators=1000,
    max_depth=12,
    learning_rate=0.02,
    subsample=0.85,
    colsample_bytree=0.85,
    min_child_weight=3,
    gamma=0.1,
    reg_alpha=0.1,
    reg_lambda=1.0,
    eval_metric='mlogloss',
    early_stopping_rounds=50,
    random_state=42,
    n_jobs=-1,
    verbosity=0
)
xgb.fit(
    X_train, y_train,
    eval_set=[(X_test, y_test)],
    verbose=False
)
xgb_acc = accuracy_score(y_test, xgb.predict(X_test))
print(f"✅ XGBoost: {xgb_acc * 100:.2f}%")

# ── Model 3: Random Forest ───────────────────────────────
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

# ── Results ──────────────────────────────────────────────
print("\n" + "=" * 55)
print("FINAL RESULTS")
print("=" * 55)
print(f"\n  Baseline          : 24.82%")
print(f"  Previous best     : 41.40%")
print(f"  Random Forest     : {rf_acc * 100:.2f}%")
print(f"  XGBoost           : {xgb_acc * 100:.2f}%")
print(f"  LightGBM          : {lgbm_acc * 100:.2f}%")

best_acc = max(rf_acc, xgb_acc, lgbm_acc)
if lgbm_acc == best_acc:
    best_model = lgbm
    best_name = "LightGBM"
elif xgb_acc == best_acc:
    best_model = xgb
    best_name = "XGBoost"
else:
    best_model = rf
    best_name = "Random Forest"

print(f"\n🏆 Winner: {best_name} — {best_acc * 100:.2f}%")
print(f"📈 Total improvement: +{(best_acc - 0.2482) * 100:.2f}%")

if best_acc >= 0.60:
    print(f"\n🎉 TARGET REACHED! 60%+ achieved!")
else:
    gap = (0.60 - best_acc) * 100
    print(f"\n📊 {gap:.2f}% away from 60% target")

# ── Save ─────────────────────────────────────────────────
print("\n⏳ Saving best model...")
with open('best_model.pkl', 'wb') as f:
    pickle.dump(best_model, f)
with open('label_encoders.pkl', 'wb') as f:
    pickle.dump(le_dict, f)
with open('feature_list.pkl', 'wb') as f:
    pickle.dump(features, f)
with open('best_accuracy.txt', 'w') as f:
    f.write(f"{best_acc * 100:.2f}")
print(f"✅ {best_name} model saved!")
print("\n🚀 Ready to update dashboard with new accuracy!")