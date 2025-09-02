"""
PyMine: An Educational Data Mining Library
Author: Fash

Core features:
- Explainable, transparent models
- What-if analysis for reasoning
- Student-friendly pseudocode mode
- No dependencies. Pure Python.
"""

# -------------------------------
# Import Key Classes & Functions
# -------------------------------

# Classifiers
from .classifiers import (
    DecisionTreeClassifier,
    NaiveBayesClassifier,
    LogisticRegressionClassifier,
    KNNClassifier
)

# Clustering
from .clustering import (
    KMeans,
    HierarchicalClustering,
    DBSCAN
)

# Anomaly Detection
from .anomaly import (
    ZScoreAnomaly,
    LOFAnomaly
)

# Association Rules
from .association import (
    Apriori
)

# Preprocessing Tools
from .preprocessing import (
    MinMaxScaler,
    ZScoreScaler,
    SimpleImputer,
    LabelEncoder,
    OneHotEncoder,
    what_if_transform
)

# Evaluation Metrics
from .evaluation import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix,
    silhouette_score,
    explain_confusion,
    explain_score,
    what_if_change_prediction
)

# Utils (only expose what makes sense for user)
from .utils import (
    train_test_split,
    z_score_normalize,
    entropy,
    gini
)


# -------------------------------
# PyMine Version Info
# -------------------------------
__version__ = '0.1.0'
__author__ = 'Fash'
__all__ = [
    # Classifiers
    'DecisionTreeClassifier', 'NaiveBayesClassifier', 'LogisticRegressionClassifier', 'KNNClassifier',

    # Clustering
    'KMeans', 'HierarchicalClustering', 'DBSCAN',

    # Anomaly Detection
    'ZScoreAnomaly', 'LOFAnomaly',

    # Association
    'Apriori',

    # Preprocessing
    'MinMaxScaler', 'ZScoreScaler', 'SimpleImputer', 'LabelEncoder', 'OneHotEncoder', 'what_if_transform',

    # Evaluation
    'accuracy_score', 'precision_score', 'recall_score', 'f1_score',
    'confusion_matrix', 'silhouette_score', 'explain_confusion', 'explain_score', 'what_if_change_prediction',

    # Utils
    'train_test_split', 'z_score_normalize', 'entropy', 'gini'
]
