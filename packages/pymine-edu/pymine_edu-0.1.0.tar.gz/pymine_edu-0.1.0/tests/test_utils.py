# tests/test_utils.py

import pandas as pd
from pymine.utils import (
    entropy, gini,
    euclidean_distance, manhattan_distance, minkowski_distance, cosine_distance,
    train_test_split, z_score_normalize,
    check_consistent_lengths, check_2d, check_numerical
)

print("\n=== UTILS MODULE TESTS WITH IRIS DATASET ===")

# Load dataset
iris_df = pd.read_csv("tests/Iris.csv")
iris_df.drop(columns=[col for col in iris_df.columns if col.lower() == "id"], inplace=True)
X = iris_df.drop(columns=['Species']).values.tolist()
y = iris_df['Species'].tolist()

# Entropy and Gini
print("\n>>> Entropy & Gini")
print(f"Entropy: {entropy(y):.4f}")
print(f"Gini Impurity: {gini(y):.4f}")

# Distance Metrics
a, b = X[0], X[1]
print("\n>>> Distance Metrics between sample 0 and 1")
print(f"Euclidean: {euclidean_distance(a, b):.4f}")
print(f"Manhattan: {manhattan_distance(a, b):.4f}")
print(f"Minkowski (p=3): {minkowski_distance(a, b):.4f}")
print(f"Cosine: {cosine_distance(a, b):.4f}")

# Train/Test Split
print("\n>>> Train-Test Split")
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3)
print(f"Train size: {len(X_train)}, Test size: {len(X_test)}")

# Z-Score Normalization
print("\n>>> Z-Score Normalization")
X_norm = z_score_normalize(X)
print(f"First normalized row: {X_norm[0]}")
print(f"Mean of first feature after normalization: {sum(row[0] for row in X_norm) / len(X_norm):.4f}")

# Validation Checks
print("\n>>> Data Validation Checks")
try:
    check_consistent_lengths(X, y)
    check_2d(X)
    check_numerical(X)
    print("All validation checks passed.")
except Exception as e:
    print(f"Validation failed: {e}")
