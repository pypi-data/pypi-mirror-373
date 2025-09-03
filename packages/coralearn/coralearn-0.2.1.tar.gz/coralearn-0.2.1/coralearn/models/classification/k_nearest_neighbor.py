import numpy as np
from collections import Counter


class KNNModel:
    def __init__(self, k=3):
        self.y_train = None
        self.X_train = None
        self.k = k

    def fit(self, X, y):
        # assign values
        self.X_train = X
        self.y_train = y

    def distance(self, a, b):
        # simple l2 distance function
        return np.sqrt(np.sum((a - b) ** 2))

    def predict(self, X):
        final_preds = []

        for x_test in X:
            # get a list with indexes and the l2 distance of each Xtrain object from the current one
            distances = [(i, self.distance(x_test, x_train)) for i, x_train in enumerate(self.X_train)]

            # sort the list and keep only the first k elements (the neightbors)
            top_k = sorted(distances, key=lambda pair: pair[1])[:self.k]

            # keep only the labels
            top_k_labels = [self.y_train[i] for i, _ in top_k]

            # find the most common using the counter library and append it
            most_common = Counter(top_k_labels).most_common(1)[0][0]
            final_preds.append(most_common)

        return final_preds
