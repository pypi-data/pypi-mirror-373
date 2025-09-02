import pandas as pd
from sklearn.model_selection import train_test_split
from pymine.classifiers import (
    DecisionTreeClassifier,
    KNNClassifier,
    NaiveBayesClassifier,
    LogisticRegressionClassifier
)

# Load your dataset
df = pd.read_csv("tests/iris.csv")
df.drop("Id", axis=1, inplace=True)
df["Species"] = df["Species"].astype("category").cat.codes  # Encode target labels

# Split into features and target
X = df.drop("Species", axis=1).values
y = df["Species"].values

# Train-test split
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# Initialize classifiers
dt = DecisionTreeClassifier(max_depth=3, mode='student')
knn = KNNClassifier(k=3)
nb = NaiveBayesClassifier()
lr = LogisticRegressionClassifier(lr=0.1, epochs=300)

# Fit models
dt.fit(X_train, y_train)
knn.fit(X_train, y_train)
nb.fit(X_train, y_train)
lr.fit(X_train, y_train)

# Evaluate models
print("Decision Tree Accuracy:", dt.score(X_test, y_test))
print("KNN Accuracy:", knn.score(X_test, y_test))
print("Naive Bayes Accuracy:", nb.score(X_test, y_test))
print("Logistic Regression Accuracy:", lr.score(X_test, y_test))

# Optional: show explainability for one example
sample = X_test[0]
print("\nExplain Decision Tree:")
print(dt.explain(sample, mode='pseudocode'))

print("\nWhat if analysis (Decision Tree):")
print(dt.what_if({0: sample[0]}, {0: sample[0] + 0.5}))
