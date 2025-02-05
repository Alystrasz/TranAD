import sys

class FastLinearInterpolation:
    def __init__(self):
        self.firstStartingTimeRaw: float = -1
        self.listOldModels = []
        self.currentStartingTimeRaw: float = 0
        self.currentStartingValueRaw: float = 0
        self.currentA: float = 0
        self.maxPossibleA: float = sys.float_info.max
        self.minPossibleA: float = sys.float_info.min
        self.lastTimeRaw: float = 0
        self.lastValueRaw: float = 0
        self.maxError: float = 0
        self.pointsCount: int = 0
        self.segmentsCount: int = 0


    def setError(self, value: float) -> None:
        self.maxError = value

    def add(self, tRaw: float, vRaw: float):
        if self.firstStartingTimeRaw == -1:
            self.firstStartingTimeRaw = tRaw
            self._initModel(tRaw, vRaw)
            return

        tNorm: float = tRaw - self.currentStartingTimeRaw;
        vNorm: float = vRaw - self.currentStartingValueRaw;
        A: float = vNorm / tNorm;

        # If the points fits, we update the values and return.
        if A <= self.maxPossibleA and A >= self.minPossibleA:
            self.minPossibleA = max(self.minPossibleA, (vNorm - self.maxError) / tNorm)
            self.maxPossibleA = min(self.maxPossibleA, (vNorm + self.maxError) / tNorm)
            self.lastTimeRaw = tRaw
            self.lastValueRaw = vRaw
            self.currentA = A
            self.pointsCount += 1
            return

        # If the point does not fit, it means that the new interpolation would end
        # up raising an error on at least one of the previous points: we keep the
        # current interpolation and start a new model.
        self.listOldModels.append((self.currentStartingTimeRaw, self.currentStartingValueRaw, self.currentA, self.pointsCount, self.segmentsCount))

        # The new interpolation starts with the last point of the previous model
        self.currentStartingTimeRaw = self.lastTimeRaw
        self.currentStartingValueRaw = self.lastValueRaw
        tNorm = tRaw - self.lastTimeRaw
        vNorm = vRaw - self.lastValueRaw
        A = vNorm / tNorm
        self.pointsCount = 1
        self.segmentsCount += 1

        # In this case, the error is 0 for all the points, so we update the model.
        self.minPossibleA = (vNorm - self.maxError) / tNorm

        # There are no other points, so no max.
        self.maxPossibleA = (vNorm + self.maxError) / tNorm

        # Idem.
        self.lastTimeRaw = tRaw
        self.lastValueRaw = vRaw
        self.currentA = A

    def _initModel(self, tRaw: float, vRaw: float) -> None:
        self.currentStartingTimeRaw = tRaw;
        self.currentStartingValueRaw = vRaw;
        self.currentA = 0;
        self.maxPossibleA = sys.float_info.max
        self.minPossibleA = sys.float_info.min
        self.lastTimeRaw = tRaw;
        self.lastValueRaw = vRaw;
        self.pointsCount = 1
        self.segmentsCount = 1

    def read(self, t: float) -> float:
        # If the reading time is before the time of the first model, we throw.
        if self.firstStartingTimeRaw == -1 or t < self.firstStartingTimeRaw:
            raise IndexError("Error the time is unavailable")

        if self.currentStartingTimeRaw <= t:
            return self._getValue(t, self.currentStartingTimeRaw, self.currentA, self.currentStartingValueRaw);

        if len(self.listOldModels) == 0:
            raise IndexError("Error the time is unavailable (!)")

        index: int = self._getIndexRead(t);
        model = self.listOldModels[index];
        return self._getValue(t, model[0], model[2], model[1])

    def _getIndexRead(self, t: float) -> int:
        minIndex: int = 0
        maxIndex: int = len(self.listOldModels) - 1
        index: int = -1
        tIndex: float

        while minIndex <= maxIndex:
            # index = (maxIndex + minIndex) ~/ 2
            index = (maxIndex + minIndex) // 2
            if minIndex == maxIndex:
                break

            tIndex = self.listOldModels[index][0]
            if t == tIndex:
                break

            if t > tIndex and t < self.listOldModels[index + 1][0]:
                break

            if t < tIndex:
                maxIndex = index - 1
            else:
                minIndex = index + 1

        return index

    def _getValue(self, t: float, T: float, A: float, B: float) -> float:
        return (A * (t - T) + B)

    def data(self):
        points = list(map(lambda t: (t[0], t[1]), self.listOldModels))

        # Hacky, but somehow works
        points.append((self.currentStartingTimeRaw, self.currentStartingValueRaw))
        points.append((self.lastTimeRaw, self.lastValueRaw, self.currentA))
        
        return points

    def get_modeled_points_counts(self):
        points = list(map(lambda t: (t[0], t[3]), self.listOldModels))

        # Hacky, but somehow works
        points.append((self.currentStartingTimeRaw, self.pointsCount))
        points.append((self.lastTimeRaw, self.pointsCount))
        
        return points

    def get_segments_counts(self):
        points = list(map(lambda t: (t[0], t[4]), self.listOldModels))

        # Hacky, but somehow works
        points.append((self.currentStartingTimeRaw, self.segmentsCount))
        points.append((self.lastTimeRaw, self.segmentsCount))
        
        return points