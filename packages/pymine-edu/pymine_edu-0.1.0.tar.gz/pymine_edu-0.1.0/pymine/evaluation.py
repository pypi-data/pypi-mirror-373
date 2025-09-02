"""
PyMine Evaluation Module
Provides core evaluation functions for classification and clustering.
Includes human-readable explainability, pseudocode mode, what-if scenarios,
and student-focused verbose logging for transparency.
"""

from collections import Counter
import math

# ---------------------------- Classification Metrics ----------------------------

def accuracy_score(y_true, y_pred):
    correct = sum(yt == yp for yt, yp in zip(y_true, y_pred))
    return correct / len(y_true)

def precision_score(y_true, y_pred, average='macro'):
    labels = set(y_true)
    precisions = []
    for label in labels:
        tp = sum((yt == yp == label) for yt, yp in zip(y_true, y_pred))
        fp = sum((yt != label and yp == label) for yt, yp in zip(y_true, y_pred))
        precisions.append(tp / (tp + fp + 1e-8))
    return sum(precisions) / len(precisions)

def recall_score(y_true, y_pred, average='macro'):
    labels = set(y_true)
    recalls = []
    for label in labels:
        tp = sum((yt == yp == label) for yt, yp in zip(y_true, y_pred))
        fn = sum((yt == label and yp != label) for yt, yp in zip(y_true, y_pred))
        recalls.append(tp / (tp + fn + 1e-8))
    return sum(recalls) / len(recalls)

def f1_score(y_true, y_pred, average='macro'):
    precision = precision_score(y_true, y_pred, average)
    recall = recall_score(y_true, y_pred, average)
    return 2 * precision * recall / (precision + recall + 1e-8)

def confusion_matrix(y_true, y_pred):
    labels = sorted(set(y_true + y_pred))
    matrix = {label: {l: 0 for l in labels} for label in labels}
    for yt, yp in zip(y_true, y_pred):
        matrix[yt][yp] += 1
    return matrix

# ---------------------------- Clustering Metrics ----------------------------

def silhouette_score(X, labels):
    def euclidean(a, b):
        return math.sqrt(sum((ai - bi) ** 2 for ai, bi in zip(a, b)))

    n = len(X)
    scores = []
    for i in range(n):
        xi = X[i]
        label_i = labels[i]
        same_cluster = [X[j] for j in range(n) if labels[j] == label_i and j != i]
        other_cluster_labels = set(labels) - {label_i}

        if not same_cluster or not other_cluster_labels:
            scores.append(0)
            continue

        a = sum(euclidean(xi, xj) for xj in same_cluster) / len(same_cluster)

        b_values = []
        for other_label in other_cluster_labels:
            other_points = [X[j] for j in range(n) if labels[j] == other_label]
            if other_points:
                b_dist = sum(euclidean(xi, xj) for xj in other_points) / len(other_points)
                b_values.append(b_dist)

        b = min(b_values) if b_values else float('inf')
        score = (b - a) / max(a, b) if max(a, b) > 0 else 0
        scores.append(score)

    return sum(scores) / len(scores)

# ---------------------------- Explainable Interface ----------------------------

def explain_confusion(y_true, y_pred, mode='text'):
    cm = confusion_matrix(y_true, y_pred)
    if mode == 'pseudocode':
        return "IF predicted == actual THEN True ELSE Error"
    lines = ["Confusion Matrix:"]
    for actual in cm:
        row = [f"{actual}"] + [f"{cm[actual][pred]}" for pred in cm[actual]]
        lines.append("\t".join(row))
    return "\n".join(lines)


def explain_score(y_true, y_pred, mode='text'):
    acc = accuracy_score(y_true, y_pred)
    f1 = f1_score(y_true, y_pred)
    prec = precision_score(y_true, y_pred)
    rec = recall_score(y_true, y_pred)
    if mode == 'pseudocode':
        return "Compute TP, FP, FN, TN from predictions\nThen calculate precision, recall, and F1-score"
    return (
        f"Accuracy: {acc:.2f}\n"
        f"Precision: {prec:.2f}\n"
        f"Recall: {rec:.2f}\n"
        f"F1 Score: {f1:.2f}"
    )

# ---------------------------- What-if Analysis ----------------------------

def what_if_change_prediction(y_true, y_pred, index, new_prediction):
    original = y_pred[index]
    y_pred[index] = new_prediction
    new_cm = confusion_matrix(y_true, y_pred)
    y_pred[index] = original  # revert
    return new_cm

 