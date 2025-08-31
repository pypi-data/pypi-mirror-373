import numpy as np
from tidyms2.annotation.correspondence import split_cluster_gmm, cluster_dbscan
import matplotlib.pyplot as plt

np.random.seed(1234)
n = 200
X1 = np.random.normal(size=(n, 2))
samples = np.hstack((np.arange(n), np.arange(n)))
X2 = np.random.normal(size=(n, 2), loc=(2, 2))
X = np.vstack((X1, X2))

dbscan_labels = cluster_dbscan(X, 2.0, 50, 10000)
gmm_labels, score = split_cluster_gmm(X, samples, 2, 3.0)

fig, ax = plt.subplots()
for l in np.unique(dbscan_labels):
    ax.scatter(*X[dbscan_labels == l].T, label=l)

ax.set_xlabel("m/z")
ax.set_ylabel("Rt")
ax.legend(title="DBSCAN labels")