import pandas as pd

df = pd.read_csv('healthcare/train_data.csv')

print("Shape:", df.shape)
print("\nColumns:", df.columns.tolist())
print("\nFirst 5 rows:")
print(df.head())
print("\nBasic Info:")
print(df.info())
print("\nMissing Values:")
print(df.isnull().sum())