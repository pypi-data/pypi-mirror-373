import numpy as np
from scipy.stats import mannwhitneyu
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error

class MWUTSDZ:
    def __init__(self, windowSize=5, pThreshold=0.01, minRegionLength=50):
        self.windowSize = windowSize
        self.pThreshold = pThreshold
        self.minRegionLength = minRegionLength
        self.kneeCycle = None
        self.kneeCapacity = None
        self.regions = []
        self.pValues = []
        self.cyclePositions = []

    def _computePValues(self, cycles, capacities):
        for i in range(self.windowSize, len(capacities) - self.windowSize):
            before = capacities[i - self.windowSize:i]
            after = capacities[i:i + self.windowSize]

            if np.std(before) == 0 and np.std(after) == 0:
                pval = 1.0
            else:
                _, pval = mannwhitneyu(before, after, alternative="two-sided")

            self.pValues.append(pval)
            self.cyclePositions.append(cycles[i])

    def _detectRegions(self):
        sigMask = np.array(self.pValues) < self.pThreshold
        start = None
        for i, sig in enumerate(sigMask):
            if sig:
                if start is None:
                    start = i
            else:
                if start is not None and i - start >= self.minRegionLength:
                    self.regions.append((self.cyclePositions[start], self.cyclePositions[i - 1]))
                start = None
        if start is not None and len(self.cyclePositions) - start >= self.minRegionLength:
            self.regions.append((self.cyclePositions[start], self.cyclePositions[-1]))

    def _detectKnee(self, cycles, capacities):
        if not self.regions:
            return
        segments = []
        for start, end in self.regions:
            mask = (cycles >= start) & (cycles <= end)
            segments.append((cycles[mask], capacities[mask]))

        x = np.concatenate([seg[0] for seg in segments])
        y = np.concatenate([seg[1] for seg in segments])

        errors = [self._fitError(x, y, i) for i in range(10, len(x) - 10)]
        bestIdx = np.argmin(errors)
        self.kneeCycle = x[bestIdx]
        self.kneeCapacity = y[bestIdx]

    def _fitError(self, x, y, idx):
        model1 = LinearRegression().fit(x[:idx].reshape(-1, 1), y[:idx])
        model2 = LinearRegression().fit(x[idx:].reshape(-1, 1), y[idx:])
        y1_pred = model1.predict(x[:idx].reshape(-1, 1))
        y2_pred = model2.predict(x[idx:].reshape(-1, 1))
        return np.sqrt(mean_squared_error(y[:idx], y1_pred)) + np.sqrt(mean_squared_error(y[idx:], y2_pred))

    def fit(self, cycles, capacities):
        cycles = np.array(cycles)
        capacities = np.array(capacities)

        if len(cycles) != len(capacities):
            raise ValueError("Length mismatch between cycles and capacities.")

        self._computePValues(cycles, capacities)
        self._detectRegions()
        self._detectKnee(cycles, capacities)

        return {
            "kneeCycle": self.kneeCycle,
            "kneeCapacity": self.kneeCapacity,
            "regions": self.regions,
            "pValues": self.pValues,
            "cyclePositions": self.cyclePositions,
        }
