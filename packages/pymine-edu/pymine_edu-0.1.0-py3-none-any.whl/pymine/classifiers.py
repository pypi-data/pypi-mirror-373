"""
PyMine Classifiers Module
--------------------------
This module implements interpretable, educational-first classifiers with explainability,
teaching-mode verbosity, what-if analysis, and pseudocode insights.

Included Models:
- DecisionTreeClassifier
- NaiveBayesClassifier
- LogisticRegressionClassifier
- KNNClassifier

Core Features:
- BaseClassifier interface
- .explain(x), .explain_prediction(y), .what_if(x, changes)
- Teaching mode for verbose step-by-step insights
"""

import math
import numpy as np
from collections import Counter, defaultdict

class BaseClassifier:
    def fit(self, X, y): raise NotImplementedError
    def predict(self, X): raise NotImplementedError
    def predict_proba(self, X): raise NotImplementedError
    def score(self, X, y):
        preds = self.predict(X)
        return sum(p == t for p, t in zip(preds, y)) / len(y)
    def explain(self, x, **kwargs): raise NotImplementedError
    def explain_prediction(self, y): raise NotImplementedError
    def what_if(self, x_dict, changes_dict):
        """
        Perform what-if analysis by modifying features in x_dict.
        Accepts: x_dict = {feature_idx: value}
                changes_dict = {feature_idx: new_value}
        Returns prediction before and after change.
        """
        # Convert dict to list based on number of features
        x = [0] * self.n_features
        for idx, val in x_dict.items():
            x[idx] = val
        x_changed = x.copy()
        for idx, val in changes_dict.items():
            x_changed[idx] = val

        original = self.predict([x])[0]
        changed = self.predict([x_changed])[0]
        return {
            "original_input": x,
            "changed_input": x_changed,
            "original_prediction": original,
            "new_prediction": changed,
            "changed": original != changed
        }


# ----------------------
# DECISION TREE CLASSIFIER
# ----------------------
class TreeNode:
    def __init__(self, feature=None, threshold=None, left=None, right=None, value=None):
        self.feature = feature
        self.threshold = threshold
        self.left = left
        self.right = right
        self.value = value

    def is_leaf(self): return self.value is not None

class DecisionTreeClassifier(BaseClassifier):
    def __init__(self, max_depth=5, min_samples_split=2, mode=None):
        self.max_depth = max_depth
        self.min_samples_split = min_samples_split
        self.root = None
        self.mode = mode  # 'student' for teaching verbosity

    def _entropy(self, y):
        total = len(y)
        counts = Counter(y)
        return -sum((c/total)*math.log2(c/total) for c in counts.values())

    def _info_gain(self, y, left_y, right_y):
        return self._entropy(y) - (
            len(left_y)/len(y)*self._entropy(left_y) + len(right_y)/len(y)*self._entropy(right_y))

    def _best_split(self, X, y):
        best_gain = -1
        best_feat, best_thresh = None, None
        for feat in range(len(X[0])):
            thresholds = set(x[feat] for x in X)
            for t in thresholds:
                left_y = [y[i] for i in range(len(X)) if X[i][feat] <= t]
                right_y = [y[i] for i in range(len(X)) if X[i][feat] > t]
                if not left_y or not right_y:
                    continue
                gain = self._info_gain(y, left_y, right_y)
                if gain > best_gain:
                    best_gain, best_feat, best_thresh = gain, feat, t
        return best_feat, best_thresh

    def _build(self, X, y, depth):
        if depth >= self.max_depth or len(set(y)) == 1:
            return TreeNode(value=Counter(y).most_common(1)[0][0])
        feat, thresh = self._best_split(X, y)
        if feat is None:
            return TreeNode(value=Counter(y).most_common(1)[0][0])
        left_idx = [i for i in range(len(X)) if X[i][feat] <= thresh]
        right_idx = [i for i in range(len(X)) if X[i][feat] > thresh]
        left = self._build([X[i] for i in left_idx], [y[i] for i in left_idx], depth+1)
        right = self._build([X[i] for i in right_idx], [y[i] for i in right_idx], depth+1)
        return TreeNode(feat, thresh, left, right)

    def fit(self, X, y):
        self.n_features = len(X[0])             # to store how many input features exist
        self.classes = sorted(set(y))           # to store unique class labels in sorted order
        self.root = self._build(X, y, 0)        # to build the decision tree


    def _predict_node(self, x, node):
        if node.is_leaf(): return node.value
        if self.mode == 'student':
            print(f"If feature[{node.feature}] <= {node.threshold} → {'left' if x[node.feature] <= node.threshold else 'right'}")
        return self._predict_node(x, node.left if x[node.feature] <= node.threshold else node.right)

    def predict(self, X):
        return [self._predict_node(x, self.root) for x in X]

    def explain(self, x, mode='logic'):
        node = self.root
        explanation = []
        while not node.is_leaf():
            if mode == 'pseudocode':
                explanation.append(f"If feature[{node.feature}] <= {node.threshold} → go left")
            else:
                explanation.append((node.feature, node.threshold, x[node.feature]))
            node = node.left if x[node.feature] <= node.threshold else node.right
        explanation.append(f"Predict: {node.value}")
        return explanation

    def explain_prediction(self, y_hat):
        result = []
        def trace(node, path):
            if node.is_leaf():
                if node.value == y_hat:
                    result.append(path[:])
                return
            path.append((node.feature, node.threshold, 'left'))
            trace(node.left, path)
            path.pop()
            path.append((node.feature, node.threshold, 'right'))
            trace(node.right, path)
            path.pop()
        trace(self.root, [])
        return result
 
# ----------------------
# NAIVE BAYES CLASSIFIER
# ----------------------
class NaiveBayesClassifier(BaseClassifier):
    def __init__(self, alpha=1.0):
        self.alpha = alpha  # Laplace smoothing

    def fit(self, X, y):
        X = np.array(X)
        y = np.array(y)
        self.classes = np.unique(y)
        self.class_probs = {c: np.sum(y == c) / len(y) for c in self.classes}
        self.feature_probs = {}

        for c in self.classes:
            self.feature_probs[c] = {}
            X_c = X[y == c]

            for feat in range(X.shape[1]):
                col = X_c[:, feat]
                values, counts = np.unique(col, return_counts=True)
                total = counts.sum()
                probs = {}

                for val in np.unique(X[:, feat]):  # All possible values
                    count = counts[values.tolist().index(val)] if val in values else 0
                    probs[val] = (count + self.alpha) / (total + self.alpha * len(np.unique(X[:, feat])))

                self.feature_probs[c][feat] = probs

    def predict(self, X):
        return [self._predict_one(x) for x in X]

    def _predict_one(self, x):
        scores = {}
        for c in self.classes:
            prob = self.class_probs[c]
            for i, val in enumerate(x):
                prob *= self.feature_probs[c][i].get(val, 1e-6)
            scores[c] = prob
        return max(scores, key=scores.get)

    def explain(self, x):
        explanation = {}
        for c in self.classes:
            probs = [self.feature_probs[c][i].get(val, 1e-6) for i, val in enumerate(x)]
            explanation[c] = (self.class_probs[c], probs)
        return explanation

    def explain_prediction(self, y_hat):
        return f"Typical feature values leading to '{y_hat}' would have high conditional probabilities for that class."

# ----------------------
# LOGISTIC REGRESSION CLASSIFIER
# ----------------------
class LogisticRegressionClassifier(BaseClassifier):
    def __init__(self, lr=0.1, epochs=100):
        self.lr = lr
        self.epochs = epochs

    def fit(self, X, y):
        self.weights = [0.0] * (len(X[0]) + 1)  # Bias + features
        for _ in range(self.epochs):
            for xi, yi in zip(X, y):
                pred = self._sigmoid(self._linear(xi))
                error = yi - pred
                self.weights[0] += self.lr * error  # bias
                for j in range(len(xi)):
                    self.weights[j+1] += self.lr * error * xi[j]

    def _linear(self, x):
        return self.weights[0] + sum(w*xj for w, xj in zip(self.weights[1:], x))

    def _sigmoid(self, z): return 1 / (1 + math.exp(-z))

    def predict(self, X):
        return [int(self._sigmoid(self._linear(x)) >= 0.5) for x in X]

    def explain(self, x):
        z = self._linear(x)
        return {f"w{i}": w for i, w in enumerate(self.weights)}, f"z = {z:.4f} → sigmoid = {self._sigmoid(z):.4f}"

    def explain_prediction(self, y_hat):
        return f"Prediction of {y_hat} typically occurs when linear combination w·x {'>' if y_hat==1 else '<'} 0"

# ----------------------
# K-NEAREST NEIGHBORS
# ----------------------
class KNNClassifier(BaseClassifier):
    def __init__(self, k=3):
        self.k = k

    def fit(self, X, y):
        self.X_train = X
        self.y_train = y

    def predict(self, X):
        return [self._predict_one(x) for x in X]

    def _predict_one(self, x):
        dists = [(self._euclidean(x, x_train), y) for x_train, y in zip(self.X_train, self.y_train)]
        top_k = sorted(dists)[:self.k]
        labels = [y for _, y in top_k]
        return Counter(labels).most_common(1)[0][0]

    def _euclidean(self, a, b):
        return math.sqrt(sum((ai - bi)**2 for ai, bi in zip(a, b)))

    def explain(self, x):
        dists = [(self._euclidean(x, x_train), y) for x_train, y in zip(self.X_train, self.y_train)]
        return sorted(dists)[:self.k]

    def explain_prediction(self, y_hat):
        return f"Class '{y_hat}' is chosen by majority among closest {self.k} neighbors."


