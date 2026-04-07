import numpy as np
from sklearn.ensemble import RandomForestClassifier

class MLModel:

    def __init__(self):
        self.model = RandomForestClassifier()
        self.trained = False

    def prepare(self, prices):
        X, y = [], []

        for i in range(10, len(prices)-1):
            X.append(prices[i-10:i])
            y.append(1 if prices[i+1] > prices[i] else 0)

        return np.array(X), np.array(y)

    def train(self, prices):
        X, y = self.prepare(prices)

        if len(X) > 10:
            self.model.fit(X, y)
            self.trained = True

    def predict(self, prices):
        if not self.trained:
            self.train(prices)

        if not self.trained:
            return "NEUTRAL"

        last = np.array(prices[-10:]).reshape(1, -1)
        pred = self.model.predict(last)[0]

        return "BUY" if pred == 1 else "SELL"