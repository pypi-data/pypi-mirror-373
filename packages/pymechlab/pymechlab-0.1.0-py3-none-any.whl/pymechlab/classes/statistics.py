from numpy import mean, std

from ..tools.stats import k_factor_normal


class Statistics():
    values: list[float] = None
    _n: int = None
    _kB: float = None
    _kA: float = None
    _mean: float = None
    _std: float = None
    _B: float = None
    _A: float = None

    def __init__(self, values: list[float]) -> None:
        self.values = values

    @property
    def n(self) -> int:
        if self._n is None:
            self._n = len(self.values)
        return self._n

    @property
    def kB(self) -> float:
        if self._kB is None:
            self._kB = k_factor_normal(self.n, 0.9)
        return self._kB

    @property
    def kA(self) -> float:
        if self._kA is None:
            self._kA = k_factor_normal(self.n, 0.99)
        return self._kA

    @property
    def mean(self):
        if self._mean is None:
            self._mean = mean(self.values)
        return self._mean

    @property
    def std(self):
        if self._std is None:
            self._std = std(self.values, ddof=1)
        return self._std

    @property
    def B(self):
        if self._B is None:
            self._B = self.mean - self.std*self.kB
        return self._B

    @property
    def A(self):
        if self._A is None:
            self._A = self.mean - self.std*self.kA
        return self._A
