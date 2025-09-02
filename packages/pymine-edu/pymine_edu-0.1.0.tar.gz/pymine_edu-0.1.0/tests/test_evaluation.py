# tests/test_evaluation.py

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, StandardScaler
from pymine.evaluation import (
    accuracy_score, precision_score, recall_score, f1_score,
    confusion_matrix, silhouette_score, explain_confusion,
    explain_score, what_if_change_prediction
)
from pymine.classifiers import DecisionTreeClassifier
from pymine.clustering import KMeans  # Assuming you have a clustering algorithm

print("\n=== EVALUATION MODULE TESTS WITH IRIS DATASET ===")

# ----------------------------- Load Dataset -----------------------------
df = pd.read_csv("tests/Iris.csv")
X = df.drop(columns=[col for col in df.columns if col.lower() in ['id', 'species']]).values
y = df['Species'].values

# Encode labels
y_encoded = LabelEncoder().fit_transform(y)

# Split data
X_train, X_test, y_train, y_test = train_test_split(X, y_encoded, test_size=0.3, random_state=42)

# -------------------------- Classification Metrics --------------------------
print("\n>>> CLASSIFICATION METRICS")
clf = DecisionTreeClassifier(max_depth=3)
clf.fit(X_train.tolist(), y_train.tolist())
y_pred = clf.predict(X_test.tolist())

print("Accuracy:", accuracy_score(y_test.tolist(), y_pred))
print("Precision:", precision_score(y_test.tolist(), y_pred))
print("Recall:", recall_score(y_test.tolist(), y_pred))
print("F1 Score:", f1_score(y_test.tolist(), y_pred))
print("\nConfusion Matrix:")
print(confusion_matrix(y_test.tolist(), y_pred))
print("\nExplain Confusion:")
print(explain_confusion(y_test.tolist(), y_pred, mode='text'))
print("\nExplain Score:")
print(explain_score(y_test.tolist(), y_pred, mode='text'))
print("\nPseudocode Explanation:")
print(explain_score(y_test.tolist(), y_pred, mode='pseudocode'))

# -------------------------- What-If Analysis --------------------------
print("\n>>> WHAT-IF ANALYSIS ON CLASSIFICATION")
index_to_change = 0
new_label = (y_pred[index_to_change] + 1) % 3  # simulate wrong prediction
what_if_result = what_if_change_prediction(y_test.tolist(), y_pred.copy(), index_to_change, new_label)
print("\nWhat-If Change at index 0:")
print(what_if_result)

# -------------------------- Clustering Metrics --------------------------
print("\n>>> CLUSTERING METRICS")
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

kmeans = KMeans(k=3)
kmeans.fit(X_scaled.tolist())
kmeans_labels = kmeans.predict(X_scaled.tolist())

sil_score = silhouette_score(X_scaled.tolist(), kmeans_labels)
print("Silhouette Score:", round(sil_score, 3))

print("\n=== EVALUATION TEST COMPLETE ===")
