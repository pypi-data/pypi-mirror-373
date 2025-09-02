# tests/test_preprocessing.py
import copy
import pandas as pd
import numpy as np
from pymine.preprocessing import MinMaxScaler, ZScoreScaler, SimpleImputer, LabelEncoder, OneHotEncoder, what_if_transform

print("\n=== PREPROCESSING MODULE TESTS WITH IRIS DATASET ===")

# Load the Iris dataset
iris_df = pd.read_csv("tests/Iris.csv")

# Drop ID column if it exists and isolate features and target
iris_df.drop(columns=[col for col in iris_df.columns if col.lower() == "id"], inplace=True)
X_numerical = iris_df.drop(columns=['Species']).values.tolist()
y_categorical = iris_df['Species'].tolist()

# ------------------ MinMaxScaler ------------------
print("\n>>> MinMaxScaler")
minmax = MinMaxScaler()
minmax.fit(X_numerical)
X_minmax = minmax.transform(X_numerical)
print("Sample transform:", X_minmax[0])
print("Explain:", minmax.explain(X_numerical[0]))
print("Pseudocode:", minmax.explain(X_numerical[0], mode='pseudocode'))
print("What-If:", what_if_transform(minmax, X_numerical[0], 0, 10.0))

# ------------------ ZScoreScaler ------------------
print("\n>>> ZScoreScaler")
zscaler = ZScoreScaler()
zscaler.fit(X_numerical)
X_zscore = zscaler.transform(X_numerical)
print("Sample transform:", X_zscore[0])
print("Explain:", zscaler.explain(X_numerical[0]))
print("Pseudocode:", zscaler.explain(X_numerical[0], mode='pseudocode'))
print("What-If:", what_if_transform(zscaler, X_numerical[0], 1, 5.5))

# ------------------ SimpleImputer ------------------
print("\n>>> SimpleImputer")
X_with_missing = copy.deepcopy(X_numerical)
X_with_missing[0][2] = None  # introduce missing value
imputer = SimpleImputer(strategy='mean')
imputer.fit(X_with_missing)
X_imputed = imputer.transform(X_with_missing)
print("Before:", X_with_missing[0])
print("After Imputation:", X_imputed[0])
print("Explain:", imputer.explain(X_with_missing[0]))
print("Pseudocode:", imputer.explain(X_with_missing[0], mode='pseudocode'))

# ------------------ LabelEncoder ------------------
print("\n>>> LabelEncoder")
label_encoder = LabelEncoder()
label_encoder.fit(y_categorical)
y_encoded = label_encoder.transform(y_categorical)
print("Sample Encoded:", y_encoded[:5])
print("Inverse Transform:", label_encoder.inverse_transform(y_encoded[:5]))
print("Explain:", label_encoder.explain(y_categorical[0]))

# ------------------ OneHotEncoder ------------------
print("\n>>> OneHotEncoder")
onehot = OneHotEncoder()
onehot.fit(y_categorical)
y_onehot = onehot.transform(y_categorical)
print("Sample One-Hot:", y_onehot[0])
print("Explain:", onehot.explain(y_categorical[0]))

print("\n=== PREPROCESSING TEST COMPLETE ===")
