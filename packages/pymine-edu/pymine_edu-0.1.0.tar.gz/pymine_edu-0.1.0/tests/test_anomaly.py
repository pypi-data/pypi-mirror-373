# tests/test_anomaly.py

import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from pymine.anomaly import ZScoreAnomaly, LOFAnomaly

# Load Iris.csv from tests folder
df = pd.read_csv("tests/Iris.csv")

# Drop non-feature columns if present (like Id or Species)
X = df.drop(columns=[col for col in df.columns if col.lower() in ['id', 'species']]).values

# Scale the features
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# Sample data point
sample = X_scaled[0]

print("\n=== Z-SCORE ANOMALY DETECTOR ===")
z_model = ZScoreAnomaly(threshold=2.5, mode='student', verbose=True)
z_model.fit(X_scaled)
z_preds = z_model.predict(X_scaled)
print("Sample prediction:", z_model.predict([sample])[0])
print(z_model.explain(sample, mode='text'))
print(z_model.explain(sample, mode='pseudocode'))
print(z_model.explain_prediction(z_preds[0]))
print(z_model.what_if(sample, 2, sample[2] + 3))  # simulate change in one feature

print("\n=== LOF ANOMALY DETECTOR ===")
lof_model = LOFAnomaly(k=5, threshold=1.5, mode='student', verbose=True)
lof_model.fit(X_scaled)
lof_preds = lof_model.predict(X_scaled)
print("Sample prediction:", lof_model.predict([sample])[0])
print(lof_model.explain(sample, mode='text'))
print(lof_model.explain(sample, mode='pseudocode'))
print(lof_model.explain_prediction(lof_preds[0]))
print(lof_model.what_if(sample, 2, sample[2] + 3))  # simulate change in one feature
