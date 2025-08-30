import numpy as np
from scipy.stats import mannwhitneyu

class MWUTSDZ:
    def __init__(self, windowSize=5, pThreshold=0.01, minRegionLength=50):
        """
        MWUT-SDZ : Détection de zones de dégradation statistiquement validées.
        Ne fait PAS de détection de knee point (c'est l'utilisateur qui choisit ensuite).
        
        Parameters
        ----------
        windowSize : int
            Taille de la fenêtre glissante (par défaut 5).
        pThreshold : float
            Seuil de significativité des p-values (par défaut 0.01).
        minRegionLength : int
            Longueur minimale d’une région pour être retenue (en nb de cycles).
        """
        self.windowSize = windowSize
        self.pThreshold = pThreshold
        self.minRegionLength = minRegionLength

        # Résultats
        self.regions = []
        self.pValues = []
        self.cyclePositions = []

    def _computePValues(self, cycles, capacities):
        """Calcule les p-values MWUT avec fenêtre glissante."""
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
        """Détecte les zones où les p-values < seuil pendant minRegionLength cycles consécutifs."""
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

    def fit(self, cycles, capacities):
        """
        Applique MWUT-SDZ → retourne uniquement les zones significatives.
        
        Parameters
        ----------
        cycles : array-like
            Indices de cycles.
        capacities : array-like
            Capacités correspondantes.

        Returns
        -------
        dict
            regions : list of tuples (start, end)
            pValues : list
            cyclePositions : list
        """
        cycles = np.array(cycles)
        capacities = np.array(capacities)

        if len(cycles) != len(capacities):
            raise ValueError("Length mismatch between cycles and capacities.")

        self._computePValues(cycles, capacities)
        self._detectRegions()

        return {
            "regions": self.regions,
            "pValues": self.pValues,
            "cyclePositions": self.cyclePositions,
        }
