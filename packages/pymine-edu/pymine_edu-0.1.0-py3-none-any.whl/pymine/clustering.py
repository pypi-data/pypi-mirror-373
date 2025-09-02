"""
PyMine Clustering Module with Explainability, Teaching Mode, and Reverse-Mode Logic
Author: Fash
"""

import math
import random
import numpy as np
from collections import defaultdict, Counter


class BaseClustering:
    def fit(self, X): ...
    def predict(self, X): ...
    def explain(self, x, mode='text'): ...
    def explain_prediction(self, cluster_label): ...
    def what_if(self, x, feature_index, new_value): ...


class KMeans(BaseClustering):
    def __init__(self, k=3, max_iters=100, mode='default', verbose=False):
        self.k = k
        self.max_iters = max_iters
        self.centroids = []
        self.labels_ = []
        self.mode = mode
        self.verbose = verbose

    def _distance(self, a, b):
        return math.sqrt(sum((x - y) ** 2 for x, y in zip(a, b)))

    def _assign_clusters(self, X):
        labels = []
        for x in X:
            distances = [self._distance(x, centroid) for centroid in self.centroids]
            labels.append(distances.index(min(distances)))
        return labels

    def _update_centroids(self, X, labels):
        new_centroids = []
        for i in range(self.k):
            cluster_points = [X[j] for j in range(len(X)) if labels[j] == i]
            if cluster_points:
                new_centroids.append([sum(dim)/len(dim) for dim in zip(*cluster_points)])
            else:
                new_centroids.append(random.choice(X))
        return new_centroids

    def fit(self, X):
        self.centroids = random.sample(list(X), self.k)
        for iteration in range(self.max_iters):
            labels = self._assign_clusters(X)
            new_centroids = self._update_centroids(X, labels)
            if self.verbose:
                print(f"Iteration {iteration + 1}:")
                for idx, centroid in enumerate(self.centroids):
                    print(f"  Centroid {idx}: {centroid}")
            if all(np.allclose(nc, c) for nc, c in zip(new_centroids, self.centroids)):
                break
            self.centroids = new_centroids
        self.labels_ = self._assign_clusters(X)

    def predict(self, X):
        return self._assign_clusters(X)

    def explain(self, x, mode='text'):
        label = self.predict([x])[0]
        centroid = self.centroids[label]
        if mode == 'pseudocode':
            explanation = "IF "
            conditions = [f"feature_{i} ≈ {round(ci, 2)}" for i, ci in enumerate(centroid)]
            return explanation + " AND ".join(conditions) + f" THEN cluster = {label}"
        return f"Point {x} assigned to cluster {label} based on proximity to centroid {centroid}"

    def explain_prediction(self, cluster_label):
        if 0 <= cluster_label < len(self.centroids):
            explanation = f"Typical features for cluster {cluster_label}:\n"
            explanation += "\n".join([f"  feature_{i} ≈ {round(v, 2)}" for i, v in enumerate(self.centroids[cluster_label])])
            return explanation
        return f"Cluster {cluster_label} does not exist."

    def what_if(self, x, feature_index, new_value):
        original_label = self.predict([x])[0]
        new_x = x[:]
        new_x[feature_index] = new_value
        new_label = self.predict([new_x])[0]
        return {
            "original_input": x,
            "modified_input": new_x,
            "original_cluster": original_label,
            "new_cluster": new_label,
            "changed": original_label != new_label
        }


class HierarchicalClustering(BaseClustering):
    def __init__(self, n_clusters=2, mode='default', verbose=False):
        self.n_clusters = n_clusters
        self.labels_ = []
        self.mode = mode
        self.verbose = verbose

    def _distance(self, a, b):
        return math.sqrt(sum((x - y) ** 2 for x, y in zip(a, b)))

    def _merge_closest(self, clusters):
        min_dist = float('inf')
        best_pair = (0, 1)
        for i in range(len(clusters)):
            for j in range(i + 1, len(clusters)):
                d = self._distance(clusters[i][0], clusters[j][0])
                if d < min_dist:
                    min_dist = d
                    best_pair = (i, j)
        return best_pair

    def fit(self, X):
        clusters = [[x] for x in X]
        while len(clusters) > self.n_clusters:
            i, j = self._merge_closest(clusters)
            merged = clusters[i] + clusters[j]
            centroid = [sum(dim)/len(dim) for dim in zip(*merged)]
            clusters[i] = [centroid]
            del clusters[j]
            if self.verbose:
                print(f"Merged clusters {i} and {j}, remaining: {len(clusters)}")
        self.clusters = clusters
        self.labels_ = self.predict(X)

    def predict(self, X):
        labels = []
        for x in X:
            distances = [self._distance(x, cluster[0]) for cluster in self.clusters]
            labels.append(distances.index(min(distances)))
        return labels

    def explain(self, x, mode='text'):
        label = self.predict([x])[0]
        centroid = self.clusters[label][0]
        if mode == 'pseudocode':
            explanation = "IF "
            conditions = [f"feature_{i} ≈ {round(ci, 2)}" for i, ci in enumerate(centroid)]
            return explanation + " AND ".join(conditions) + f" THEN cluster = {label}"
        return f"Point {x} is closest to cluster {label} centroid {centroid}"

    def explain_prediction(self, cluster_label):
        if 0 <= cluster_label < len(self.clusters):
            centroid = self.clusters[cluster_label][0]
            return "\n".join([f"feature_{i} ≈ {round(v, 2)}" for i, v in enumerate(centroid)])
        return f"Cluster {cluster_label} does not exist."

    def what_if(self, x, feature_index, new_value):
        original_label = self.predict([x])[0]
        new_x = x[:]
        new_x[feature_index] = new_value
        new_label = self.predict([new_x])[0]
        return {
            "original_input": x,
            "modified_input": new_x,
            "original_cluster": original_label,
            "new_cluster": new_label,
            "changed": original_label != new_label
        }


class DBSCAN(BaseClustering):
    def __init__(self, eps=0.5, min_samples=5, mode='default', verbose=False):
        self.eps = eps
        self.min_samples = min_samples
        self.labels_ = []
        self.mode = mode
        self.verbose = verbose

    def _distance(self, a, b):
        return math.sqrt(sum((x - y) ** 2 for x, y in zip(a, b)))

    def fit(self, X):
        labels = [-1] * len(X)
        cluster_id = 0
        for i in range(len(X)):
            if labels[i] != -1:
                continue
            neighbors = self._region_query(X, i)
            if len(neighbors) < self.min_samples:
                labels[i] = -1
            else:
                self._expand_cluster(X, labels, i, neighbors, cluster_id)
                cluster_id += 1
        self.labels_ = labels

    def _region_query(self, X, idx):
        neighbors = []
        for i in range(len(X)):
            if self._distance(X[idx], X[i]) <= self.eps:
                neighbors.append(i)
        return neighbors

    def _expand_cluster(self, X, labels, idx, neighbors, cluster_id):
        labels[idx] = cluster_id
        i = 0
        while i < len(neighbors):
            point_idx = neighbors[i]
            if labels[point_idx] == -1:
                labels[point_idx] = cluster_id
            elif labels[point_idx] == -1:
                labels[point_idx] = cluster_id
                more_neighbors = self._region_query(X, point_idx)
                if len(more_neighbors) >= self.min_samples:
                    neighbors.extend(more_neighbors)
            i += 1

    def predict(self, X):
        return self.labels_

    def explain(self, x, mode='text'):
        return "DBSCAN assigns based on density. Use .explain_prediction(cluster_id) for cluster insight."

    def explain_prediction(self, cluster_label):
        return f"Cluster {cluster_label}: Formed from core points with density ≥ {self.min_samples} within radius {self.eps}."

    def what_if(self, x, feature_index, new_value):
        return {
            "message": "DBSCAN is density-based. Changing one feature may or may not affect cluster membership based on neighbors."
        }
