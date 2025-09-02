"""
PyMine Anomaly Detection Module with Explainability, What-if Analysis, and Teaching Mode
Author: Fash
"""

import numpy as np
import math
from statistics import mean, stdev
from collections import Counter

class BaseAnomalyDetector:
    def fit(self, X): ...
    def predict(self, X): ...
    def explain(self, x, mode='text'): ...
    def explain_prediction(self, y_hat): ...
    def what_if(self, x, feature_index, new_value): ...


class ZScoreAnomaly(BaseAnomalyDetector):
    def __init__(self, threshold=3, mode='default', verbose=False):
        self.threshold = threshold
        self.mode = mode
        self.verbose = verbose
        self.means = []
        self.stds = []

    def fit(self, X):
        self.means = [mean(col) for col in zip(*X)]
        self.stds = [stdev(col) or 1e-8 for col in zip(*X)]
        if self.verbose or self.mode == 'student':
            print("[ZScoreAnomaly] Feature Means:", self.means)
            print("[ZScoreAnomaly] Feature STDs:", self.stds)

    def predict(self, X):
        labels = []
        for x in X:
            outlier = any(abs(x[i] - self.means[i]) / self.stds[i] > self.threshold for i in range(len(x)))
            labels.append(1 if outlier else 0)
        return labels

    def explain(self, x, mode='text'):
        scores = [(i, abs(x[i] - self.means[i]) / self.stds[i]) for i in range(len(x))]
        if mode == 'pseudocode':
            return "IF " + " OR ".join([f"zscore(feature_{i}) > {self.threshold}" for i, z in scores if z > self.threshold]) + " THEN anomaly"
        else:
            expl = [f"feature_{i} z-score = {round(z, 2)}" for i, z in scores]
            return f"Anomaly Explanation: \n" + "\n".join(expl)

    def explain_prediction(self, y_hat):
        if y_hat == 1:
            return "Anomalies typically result from one or more features having z-scores greater than the threshold."
        else:
            return "Normal points usually have all z-scores below the threshold."

    def what_if(self, x, feature_index, new_value):
        original = x[:]
        new_x = x[:]
        new_x[feature_index] = new_value
        pred_orig = self.predict([original])[0]
        pred_new = self.predict([new_x])[0]
        return {
            "original": original,
            "modified": new_x,
            "original_prediction": pred_orig,
            "new_prediction": pred_new,
            "changed": pred_orig != pred_new
        }


class LOFAnomaly(BaseAnomalyDetector):
    def __init__(self, k=5, threshold=1.5, mode='default', verbose=False):
        self.k = k
        self.threshold = threshold
        self.X_train = []
        self.mode = mode
        self.verbose = verbose

    def _distance(self, a, b):
        return math.sqrt(sum((x - y) ** 2 for x, y in zip(a, b)))

    def fit(self, X):
        self.X_train = X[:]

    def _local_density(self, x):
        distances = sorted([self._distance(x, xi) for xi in self.X_train if not np.array_equal(xi, x)])
        neighbors = distances[:self.k]
        return 1 / (sum(neighbors) / self.k + 1e-8)

    def _lof_score(self, x):
        ld_x = self._local_density(x)
        neighbor_densities = [self._local_density(n) for n in self.X_train if self._distance(x, n) < self.threshold]
        if not neighbor_densities:
            return float('inf')
        return sum(nd / ld_x for nd in neighbor_densities) / len(neighbor_densities)

    def predict(self, X):
        return [1 if self._lof_score(x) > self.threshold else 0 for x in X]

    def explain(self, x, mode='text'):
        score = self._lof_score(x)
        if mode == 'pseudocode':
            return f"IF LOF(x) > {self.threshold} THEN anomaly"
        else:
            return f"LOF score: {round(score, 3)} \u2192 {'Anomaly' if score > self.threshold else 'Normal'}"

    def explain_prediction(self, y_hat):
        if y_hat == 1:
            return "Points with Local Outlier Factor above the threshold are flagged as anomalies."
        else:
            return "Points with low LOF are considered normal, close to dense clusters."

    def what_if(self, x, feature_index, new_value):
        original = x[:]
        new_x = x[:]
        new_x[feature_index] = new_value
        pred_orig = self.predict([original])[0]
        pred_new = self.predict([new_x])[0]
        return {
            "original": original,
            "modified": new_x,
            "original_prediction": pred_orig,
            "new_prediction": pred_new,
            "changed": pred_orig != pred_new
        }


# To use:
# z = ZScoreAnomaly(threshold=2.5, mode='student', verbose=True)
# z.fit(data)
# print(z.predict([some_point]))
# print(z.explain(some_point, mode='pseudocode'))
# print(z.what_if(some_point, 2, new_val))
