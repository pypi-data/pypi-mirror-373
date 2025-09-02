"""
Preprocessing utilities module for PyMine
Includes scalers, imputers, encoders, and explainable transformations
"""

import math
import copy
from collections import Counter

class BaseTransformer:
    def fit(self, X): ...
    def transform(self, X): ...
    def fit_transform(self, X):
        self.fit(X)
        return self.transform(X)
    def explain(self, x, mode='text'): ...

class MinMaxScaler(BaseTransformer):
    def __init__(self):
        self.mins = []
        self.maxs = []

    def fit(self, X):
        self.mins = [min(col) for col in zip(*X)]
        self.maxs = [max(col) for col in zip(*X)]

    def transform(self, X):
        return [[(x[i] - self.mins[i]) / (self.maxs[i] - self.mins[i] + 1e-8)
                 for i in range(len(x))] for x in X]

    def explain(self, x, mode='text'):
        if mode == 'pseudocode':
            return "\n".join([f"scaled_{i} = (x_{i} - min_{i}) / (max_{i} - min_{i})" 
                             for i in range(len(x))])
        return f"Scaled using min={self.mins} and max={self.maxs}"

class ZScoreScaler(BaseTransformer):
    def __init__(self):
        self.means = []
        self.stds = []

    def fit(self, X):
        self.means = [sum(col) / len(col) for col in zip(*X)]
        self.stds = [math.sqrt(sum((x - mean)**2 for x in col) / len(col)) 
                     for col, mean in zip(zip(*X), self.means)]

    def transform(self, X):
        return [[(x[i] - self.means[i]) / (self.stds[i] + 1e-8)
                 for i in range(len(x))] for x in X]

    def explain(self, x, mode='text'):
        if mode == 'pseudocode':
            return "\n".join([f"z_{i} = (x_{i} - mean_{i}) / std_{i}" for i in range(len(x))])
        return f"Z-score scaled with means={self.means}, stds={self.stds}"

class SimpleImputer(BaseTransformer):
    def __init__(self, strategy='mean'):
        self.strategy = strategy
        self.fill_values = []

    def fit(self, X):
        for col in zip(*X):
            values = [x for x in col if x is not None]
            if self.strategy == 'mean':
                self.fill_values.append(sum(values) / len(values))
            elif self.strategy == 'median':
                sorted_vals = sorted(values)
                n = len(sorted_vals)
                mid = n // 2
                median = (sorted_vals[mid] if n % 2 != 0 
                          else (sorted_vals[mid - 1] + sorted_vals[mid]) / 2)
                self.fill_values.append(median)
            elif self.strategy == 'mode':
                most_common = Counter(values).most_common(1)[0][0]
                self.fill_values.append(most_common)
            else:
                raise ValueError("Unsupported strategy")

    def transform(self, X):
        return [[self.fill_values[i] if x is None else x for i, x in enumerate(row)] for row in X]

    def explain(self, x, mode='text'):
        if mode == 'pseudocode':
            return "\n".join([f"x_{i} = {self.fill_values[i]} if x_{i} is None else x_{i}"
                             for i in range(len(x))])
        return f"Filled missing with strategy={self.strategy}, values={self.fill_values}"

class LabelEncoder(BaseTransformer):
    def __init__(self):
        self.mapping = {}
        self.reverse_mapping = {}

    def fit(self, X):
        unique_values = set(X)
        self.mapping = {val: i for i, val in enumerate(unique_values)}
        self.reverse_mapping = {i: val for val, i in self.mapping.items()}

    def transform(self, X):
        return [self.mapping[val] for val in X]

    def inverse_transform(self, X):
        return [self.reverse_mapping[val] for val in X]

    def explain(self, x, mode='text'):
        return f"Encoded '{x}' as {self.mapping.get(x, '?')}"

class OneHotEncoder(BaseTransformer):
    def __init__(self):
        self.unique_values = []

    def fit(self, X):
        self.unique_values = list(set(X))

    def transform(self, X):
        return [[1 if x == val else 0 for val in self.unique_values] for x in X]

    def explain(self, x, mode='text'):
        one_hot = [1 if x == val else 0 for val in self.unique_values]
        return f"{x} encoded as one-hot vector: {one_hot}"

# Extra utility to show what-if transformation for a row

def what_if_transform(transformer, x, index, new_value):
    original = transformer.transform([x])[0]
    x_new = x[:]
    x_new[index] = new_value
    modified = transformer.transform([x_new])[0]
    return {
        'original_input': x,
        'transformed': original,
        'modified_input': x_new,
        'transformed_modified': modified,
        'difference': [a - b for a, b in zip(original, modified)]
    }

__all__ = [
    'MinMaxScaler',
    'ZScoreScaler',
    'SimpleImputer',
    'LabelEncoder',
    'OneHotEncoder',
    'what_if_transform'
]
