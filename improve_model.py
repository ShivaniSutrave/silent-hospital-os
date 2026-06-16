import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import accuracy_score, classification_report
from xgboost import XGBClassifier
import warnings
warnings.filterwarnings('ignore')

print("Loading real hospital data...")
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
    'Available Extra Rooms in Hospital'
]

le_dict = {}
df_model = df[features + ['Stay']].copy()

for col in ['Department', 'Severity of Illness',
            'Type of Admission', 'Age',
            'Ward_Type', 'Stay']:
    le = LabelEncoder()
    df_model[col] = le.fit_transform(df_model[col])
    le_dict[col] = le

X = df_model[features]
y = df_model['Stay']

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42)

# ── Random Forest ────────────────────────────────────────
print("\n" + "=" * 50)
print("Model 1: Random Forest")
print("=" * 50)
rf = RandomForestClassifier(
    n_estimators=200,
    max_depth=15,
    random_state=42,
    n_jobs=-1
)
rf.fit(X_train, y_train)
rf_acc = accuracy_score(y_test, rf.predict(X_test))
print(f"✅ Accuracy: {rf_acc * 100:.2f}%")

# ── XGBoost ──────────────────────────────────────────────
print("\n" + "=" * 50)
print("Model 2: XGBoost (Upgraded)")
print("=" * 50)
xgb = XGBClassifier(
    n_estimators=300,
    max_depth=8,
    learning_rate=0.1,
    use_label_encoder=False,
    eval_metric='mlogloss',
    random_state=42,
    n_jobs=-1
)
xgb.fit(X_train, y_train)
xgb_acc = accuracy_score(y_test, xgb.predict(X_test))
print(f"✅ Accuracy: {xgb_acc * 100:.2f}%")

# ── Winner ───────────────────────────────────────────────
print("\n" + "=" * 50)
print("RESULTS COMPARISON")
print("=" * 50)
print(f"\n  Random Forest : {rf_acc * 100:.2f}%")
print(f"  XGBoost       : {xgb_acc * 100:.2f}%")

if xgb_acc > rf_acc:
    print(f"\n🏆 XGBoost wins!")
    improvement = (xgb_acc - rf_acc) * 100
    print(f"   Improved by {improvement:.2f}% over Random Forest")
else:
    print(f"\n🏆 Random Forest wins!")

# ── Feature Importance ───────────────────────────────────
print("\n" + "=" * 50)
print("Top Features That Predict Patient Stay")
print("=" * 50)
importances = pd.Series(
    xgb.feature_importances_, index=features
).sort_values(ascending=False)

print()
for feat, score in importances.items():
    bar = "█" * int(score * 100)
    print(f"  {feat:<35} {bar} {score:.3f}")