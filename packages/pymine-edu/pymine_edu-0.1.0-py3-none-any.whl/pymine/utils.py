"""
utils.py - PyMine Utility Module

This module contains helper functions and shared logic used across the PyMine library.
It includes mathematical computations, distance metrics, entropy/gini calculations,
logging utilities, data validation helpers, and other reusable components.

These utilities are intended to promote clean architecture, modularity, and clarity.
All functions are built with educational readability in mind.
"""

import math
from collections import Counter

# ================================
# MATHEMATICAL / INFORMATION THEORY FUNCTIONS
# ================================

def entropy(y):
    """
    Calculate the entropy of a list of labels.

    Args:
        y (list): Target class labels

    Returns:
        float: Entropy value
    """
    total = len(y)
    counts = Counter(y)
    return -sum((count / total) * math.log2(count / total)
               for count in counts.values() if count > 0)

def gini(y):
    """
    Calculate the Gini impurity of a list of labels.

    Args:
        y (list): Target class labels

    Returns:
        float: Gini impurity
    """
    total = len(y)
    counts = Counter(y)
    return 1.0 - sum((count / total) ** 2 for count in counts.values())


# ================================
# DISTANCE METRICS (For KNN and Clustering)
# ================================

def euclidean_distance(a, b):
    """Calculate Euclidean distance between two vectors"""
    return math.sqrt(sum((x - y) ** 2 for x, y in zip(a, b)))

def manhattan_distance(a, b):
    """Calculate Manhattan (L1) distance between two vectors"""
    return sum(abs(x - y) for x, y in zip(a, b))

def minkowski_distance(a, b, p=3):
    """Calculate Minkowski distance between two vectors"""
    return sum(abs(x - y) ** p for x, y in zip(a, b)) ** (1 / p)

def cosine_distance(a, b):
    """Calculate Cosine distance between two vectors"""
    dot_product = sum(x * y for x, y in zip(a, b))
    mag_a = math.sqrt(sum(x ** 2 for x in a))
    mag_b = math.sqrt(sum(y ** 2 for y in b))
    if mag_a == 0 or mag_b == 0:
        return 1.0  # Maximum distance if either vector is zero
    cosine_sim = dot_product / (mag_a * mag_b)
    return 1 - cosine_sim


# ================================
# DATA SPLITTING & NORMALIZATION
# ================================

def train_test_split(X, y, test_size=0.2):
    """
    Split dataset into training and testing subsets

    Args:
        X (list): Features
        y (list): Labels
        test_size (float): Proportion of test data

    Returns:
        tuple: X_train, X_test, y_train, y_test
    """
    from random import shuffle
    data = list(zip(X, y))
    shuffle(data)
    split_idx = int(len(data) * (1 - test_size))
    train, test = data[:split_idx], data[split_idx:]
    X_train, y_train = zip(*train)
    X_test, y_test = zip(*test)
    return list(X_train), list(X_test), list(y_train), list(y_test)

def z_score_normalize(X):
    """
    Apply z-score normalization (standardization) to features

    Args:
        X (list of list): 2D array of features

    Returns:
        list of list: Normalized features
    """
    transposed = list(zip(*X))
    normalized = []
    for feature in transposed:
        mean = sum(feature) / len(feature)
        std = math.sqrt(sum((x - mean) ** 2 for x in feature) / len(feature))
        std = std if std > 0 else 1e-8
        normalized.append([(x - mean) / std for x in feature])
    return list(map(list, zip(*normalized)))


# ================================
# LOGGING / PRINT UTILITIES (Verbose Mode)
# ================================

def log_step(message, verbose=True):
    """
    Print a log message only if verbose mode is active

    Args:
        message (str): Message to print
        verbose (bool): Flag for logging
    """
    if verbose:
        print(f"[PyMine] {message}")


def print_ascii_tree(node, depth=0):
    """
    Recursively print a decision tree using ASCII formatting.
    Used for visualizing trees in the terminal.
    """
    indent = "  " * depth
    if hasattr(node, 'value') and node.value is not None:
        print(f"{indent}Predict: {node.value}")
    else:
        print(f"{indent}Feature {node.feature} <= {node.threshold:.4f}")
        print_ascii_tree(node.left, depth + 1)
        print(f"{indent}Feature {node.feature} > {node.threshold:.4f}")
        print_ascii_tree(node.right, depth + 1)


# ================================
# VALIDATION / SANITY CHECK HELPERS
# ================================

def check_consistent_lengths(X, y):
    if len(X) != len(y):
        raise ValueError("Mismatch in number of samples between X and y")

def check_2d(X):
    if not all(isinstance(row, (list, tuple)) for row in X):
        raise ValueError("X must be a 2D list or list of tuples")

def check_numerical(X):
    for row in X:
        for val in row:
            if not isinstance(val, (int, float)):
                raise ValueError("All feature values must be numeric")


# ================================
# EXPLAINABILITY HELPERS
# ================================

def format_explanation_dict(d):
    """
    Nicely formats an explanation dictionary into a readable string.
    Useful for .explain(x) methods.
    """
    return "\n".join(f"{k}: {v}" for k, v in d.items())


# ================================
# END OF UTILS MODULE
# ================================
