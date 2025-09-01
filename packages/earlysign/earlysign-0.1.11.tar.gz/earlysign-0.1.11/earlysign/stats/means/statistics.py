from typing import Tuple, List, Optional, Sequence, Any
import math
from earlysign.core.interface import SequentialStatistic, StatisticState, Stateful

MeanObservation = Tuple[
    float, float
]  # (observation for group 1, observation for group 2)


class TwoSampleTStatistic(
    SequentialStatistic[int, MeanObservation, float], Stateful[StatisticState]
):
    """
    Two-sample t-statistic for the difference in means. Computed online using
    Welford's algorithm for numerical stability.
    """

    def __init__(self, max_total_samples: int):
        self.max_samples = max_total_samples
        self._history: List[Tuple[int, float]] = []
        self._n1, self._n2 = 0, 0
        self._mean1, self._mean2 = 0.0, 0.0
        self._m2_1, self._m2_2 = 0.0, 0.0  # Sum of squares of differences from the mean

    @property
    def history(self) -> Sequence[Tuple[int, float]]:
        return self._history

    @property
    def current_value(self) -> Optional[float]:
        return self._history[-1][1] if self._history else None

    @property
    def current_info_metric(self) -> float:
        return float(self._n1 + self._n2)

    @property
    def max_info_metric(self) -> float:
        return float(self.max_samples)

    def update(self, time: int, observation: MeanObservation) -> None:
        x1, x2 = observation

        # Welford's algorithm for group 1
        self._n1 += 1
        delta1 = x1 - self._mean1
        self._mean1 += delta1 / self._n1
        delta2_1 = x1 - self._mean1
        self._m2_1 += delta1 * delta2_1

        # Welford's algorithm for group 2
        self._n2 += 1
        delta2 = x2 - self._mean2
        self._mean2 += delta2 / self._n2
        delta2_2 = x2 - self._mean2
        self._m2_2 += delta2 * delta2_2

        # Welch's t-test statistic calculation
        if self._n1 < 2 or self._n2 < 2:
            t_value = 0.0
        else:
            var1 = self._m2_1 / (self._n1 - 1)
            var2 = self._m2_2 / (self._n2 - 1)
            std_err = math.sqrt(var1 / self._n1 + var2 / self._n2)
            t_value = (self._mean1 - self._mean2) / std_err if std_err > 0 else 0.0

        self._history.append((time, t_value))

    def get_state(self) -> StatisticState:
        internal_state = {
            "n1": self._n1,
            "n2": self._n2,
            "mean1": self._mean1,
            "mean2": self._mean2,
            "m2_1": self._m2_1,
            "m2_2": self._m2_2,
        }
        return StatisticState(
            history=list(self._history), internal_state=internal_state
        )

    def load_state(self, state: StatisticState) -> None:
        self._history = state.history
        self._n1 = state.internal_state.get("n1", 0)
        self._n2 = state.internal_state.get("n2", 0)
        self._mean1 = state.internal_state.get("mean1", 0.0)
        self._mean2 = state.internal_state.get("mean2", 0.0)
        self._m2_1 = state.internal_state.get("m2_1", 0.0)
        self._m2_2 = state.internal_state.get("m2_2", 0.0)


class PooledTwoSampleTStatistic(
    SequentialStatistic[int, MeanObservation, float], Stateful[StatisticState]
):
    """
    Two-sample t-statistic for the difference in means (equal-variance).
    Uses pooled variance and computes online for numerical stability.
    This corresponds to the common-variance (varEqual = TRUE) t-test in the R implementation.
    """

    def __init__(self, max_total_samples: int):
        self.max_samples = max_total_samples
        self._history: List[Tuple[int, float]] = []
        self._n1, self._n2 = 0, 0
        self._mean1, self._mean2 = 0.0, 0.0
        self._m2_1, self._m2_2 = 0.0, 0.0  # Sum of squares of differences from the mean

    @property
    def history(self) -> Sequence[Tuple[int, float]]:
        return self._history

    @property
    def current_value(self) -> Optional[float]:
        return self._history[-1][1] if self._history else None

    @property
    def current_info_metric(self) -> float:
        return float(self._n1 + self._n2)

    @property
    def max_info_metric(self) -> float:
        return float(self.max_samples)

    def update(self, time: int, observation: MeanObservation) -> None:
        x1, x2 = observation

        # Welford's algorithm for group 1
        self._n1 += 1
        delta1 = x1 - self._mean1
        self._mean1 += delta1 / self._n1
        delta2_1 = x1 - self._mean1
        self._m2_1 += delta1 * delta2_1

        # Welford's algorithm for group 2
        self._n2 += 1
        delta2 = x2 - self._mean2
        self._mean2 += delta2 / self._n2
        delta2_2 = x2 - self._mean2
        self._m2_2 += delta2 * delta2_2

        # Pooled-variance t-test statistic calculation (equal variances assumed)
        if self._n1 < 2 or self._n2 < 2:
            t_value = 0.0
        else:
            var1 = self._m2_1 / (self._n1 - 1)
            var2 = self._m2_2 / (self._n2 - 1)
            # pooled variance (unbiased)
            pooled_var = ((self._n1 - 1) * var1 + (self._n2 - 1) * var2) / (
                self._n1 + self._n2 - 2
            )
            std_err = math.sqrt(pooled_var * (1.0 / self._n1 + 1.0 / self._n2))
            t_value = (self._mean1 - self._mean2) / std_err if std_err > 0 else 0.0

        self._history.append((time, t_value))

    def get_state(self) -> StatisticState:
        internal_state = {
            "n1": self._n1,
            "n2": self._n2,
            "mean1": self._mean1,
            "mean2": self._mean2,
            "m2_1": self._m2_1,
            "m2_2": self._m2_2,
        }
        return StatisticState(
            history=list(self._history), internal_state=internal_state
        )

    def load_state(self, state: StatisticState) -> None:
        self._history = state.history
        self._n1 = state.internal_state.get("n1", 0)
        self._n2 = state.internal_state.get("n2", 0)
        self._mean1 = state.internal_state.get("mean1", 0.0)
        self._mean2 = state.internal_state.get("mean2", 0.0)
        self._m2_1 = state.internal_state.get("m2_1", 0.0)
        self._m2_2 = state.internal_state.get("m2_2", 0.0)
