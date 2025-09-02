import unittest
import pandas as pd
from sklearn.preprocessing import StandardScaler

from pymine.clustering import KMeans, HierarchicalClustering, DBSCAN

class TestClusteringAlgorithms(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Load and scale Iris dataset
        df = pd.read_csv("tests/iris.csv")
        cls.X = df.iloc[:, :-1].values
        scaler = StandardScaler()
        cls.X_scaled = scaler.fit_transform(cls.X)

    def test_kmeans(self):
        model = KMeans(k=3, mode='student', verbose=True)
        model.fit(self.X_scaled)
        labels = model.predict(self.X_scaled)
        self.assertEqual(len(labels), len(self.X_scaled))

        # Explain a point
        print("\nKMeans Explain:")
        print(model.explain(self.X_scaled[0]))

        # Explain a cluster
        print("\nKMeans Cluster Profile:")
        print(model.explain_prediction(0))

        # What-If
        print("\nKMeans What-If:")
        print(model.what_if(self.X_scaled[0], 0, self.X_scaled[0][0] + 1))

    def test_hierarchical(self):
        model = HierarchicalClustering(n_clusters=3, verbose=True)
        model.fit(self.X_scaled)
        labels = model.predict(self.X_scaled)
        self.assertEqual(len(labels), len(self.X_scaled))

        print("\nHierarchical Explain:")
        print(model.explain(self.X_scaled[1]))

        print("\nHierarchical Cluster Profile:")
        print(model.explain_prediction(1))

        print("\nHierarchical What-If:")
        print(model.what_if(self.X_scaled[1], 0, self.X_scaled[1][0] + 1))

    def test_dbscan(self):
        model = DBSCAN(eps=0.8, min_samples=5)
        model.fit(self.X_scaled)
        labels = model.predict(self.X_scaled)
        self.assertEqual(len(labels), len(self.X_scaled))

        print("\nDBSCAN Explain:")
        print(model.explain(self.X_scaled[2]))

        print("\nDBSCAN Cluster Info:")
        print(model.explain_prediction(0))

        print("\nDBSCAN What-If:")
        print(model.what_if(self.X_scaled[2], 0, self.X_scaled[2][0] + 1))


if __name__ == "__main__":
    unittest.main()
