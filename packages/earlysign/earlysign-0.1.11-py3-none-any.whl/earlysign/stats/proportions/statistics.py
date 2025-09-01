from typing import Tuple, List, Optional, Sequence, Any, Dict
from scipy.special import betaln
import math
from earlysign.core.interface import (
    SequentialStatistic,
    StatisticState,
    Stateful,
)
from earlysign.stats.proportions.design import (
    SafeDesignTwoProportions,
    design_safe_two_proportions,
)


ProportionObservation = Tuple[
    int, int
]  # (success in group1 (1/0), success in group2 (1/0))


class TwoSampleZStatisticApprox(
    SequentialStatistic[int, ProportionObservation, float], Stateful[StatisticState]
):
    """
    Z-statistic for the difference in two proportions (normal approximation).
    Appropriate when sample sizes are large.
    """

    def __init__(self, max_total_samples: int):
        self.max_samples = max_total_samples
        self._history: List[Tuple[int, float]] = []
        self._n1, self._n2, self._s1, self._s2 = 0, 0, 0, 0

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

    def update(self, time: int, observation: ProportionObservation) -> None:
        obs1, obs2 = observation
        self._n1 += 1
        self._n2 += 1
        self._s1 += obs1
        self._s2 += obs2

        # Compute the statistic
        p1_hat = self._s1 / self._n1
        p2_hat = self._s2 / self._n2
        p_hat = (self._s1 + self._s2) / (self._n1 + self._n2)

        if p_hat <= 0 or p_hat >= 1:
            z_value = 0.0
        else:
            std_err = (p_hat * (1 - p_hat) * (1 / self._n1 + 1 / self._n2)) ** 0.5
            z_value = (p1_hat - p2_hat) / std_err if std_err > 0 else 0.0

        self._history.append((time, z_value))

    def get_state(self) -> StatisticState:
        internal_state = {
            "n1": self._n1,
            "n2": self._n2,
            "s1": self._s1,
            "s2": self._s2,
        }
        return StatisticState(
            history=list(self._history), internal_state=internal_state
        )

    def load_state(self, state: StatisticState) -> None:
        self._history = state.history
        self._n1 = state.internal_state.get("n1", 0)
        self._n2 = state.internal_state.get("n2", 0)
        self._s1 = state.internal_state.get("s1", 0)
        self._s2 = state.internal_state.get("s2", 0)


# --- Safe 2x2 E-value Sequential Statistic ---------------------------------
class EValueTwoProportions(
    SequentialStatistic[int, ProportionObservation, float], Stateful[StatisticState]
):
    """Sequential statistic that tracks the cumulative e-value for 2x2 blocks.

    Each call to update() accepts a tuple (succ_a_block, succ_b_block) representing
    the number of successes observed in the block for group A and B respectively.
    The statistic multiplies per-block E-values (computed via safe2x2.e_value_two_proportions)
    to form a cumulative E-value and records a time-indexed history.
    """

    def __init__(
        self,
        design: Optional["SafeDesignTwoProportions"] = None,
        max_total_samples: int = 1000,
    ) -> None:
        # Accept SafeDesignTwoProportions or create a default one
        if design is None:
            # design_safe_two_proportions returns a SafeDesignTwoProportions
            # and is compatible with the 'design' attribute type.
            self.design = design_safe_two_proportions(na=1, nb=1)
        else:
            self.design = design
        self.max_samples = max_total_samples
        self._history: List[Tuple[int, float]] = []
        self._cum_e: float = 1.0
        self._blocks: int = 0

    @property
    def history(self) -> Sequence[Tuple[int, float]]:
        return self._history

    @property
    def current_value(self) -> Optional[float]:
        return self._history[-1][1] if self._history else None

    @property
    def current_info_metric(self) -> float:
        return float(self._blocks)

    @property
    def max_info_metric(self) -> float:
        return float(self.max_samples)

    def update(self, time: int, observation: ProportionObservation) -> None:
        succ_a_block, succ_b_block = observation
        # compute block-level E-value using the private module helper
        e_block = _e_value_two_proportions(
            succ_a=int(succ_a_block),
            n_a=self.design.na,
            succ_b=int(succ_b_block),
            n_b=self.design.nb,
            design=self.design,
        )
        self._cum_e *= e_block
        self._blocks += 1
        self._history.append((time, float(self._cum_e)))

    # (block-level helper moved to module-level _e_value_two_proportions)

    def get_state(self) -> StatisticState:
        internal_state: Dict[str, Any] = {
            "cum_e": self._cum_e,
            "blocks": self._blocks,
            "design": {
                "na": self.design.na,
                "nb": self.design.nb,
                "alpha": self.design.alpha,
                "betaA1": self.design.betaA1,
                "betaA2": self.design.betaA2,
                "betaB1": self.design.betaB1,
                "betaB2": self.design.betaB2,
            },
        }
        return StatisticState(
            history=list(self._history), internal_state=internal_state
        )

    def load_state(self, state: StatisticState) -> None:
        self._history = state.history
        self._cum_e = float(state.internal_state.get("cum_e", 1.0))
        self._blocks = int(state.internal_state.get("blocks", 0))
        d = state.internal_state.get("design", {})
        if d:
            self.design = SafeDesignTwoProportions(
                na=d.get("na", self.design.na),
                nb=d.get("nb", self.design.nb),
                alpha=d.get("alpha", self.design.alpha),
                betaA1=d.get("betaA1", self.design.betaA1),
                betaA2=d.get("betaA2", self.design.betaA2),
                betaB1=d.get("betaB1", self.design.betaB1),
                betaB2=d.get("betaB2", self.design.betaB2),
                nBlocksPlan=None,
            )


# Repository-style export: name the statistic class EValueTwoProportions
# The canonical Statistic export is the class EValueTwoProportions above.


# --- Beta-Binomial / Safe2x2 helpers ---------------------------------


def _e_value_two_proportions(
    succ_a: int,
    n_a: int,
    succ_b: int,
    n_b: int,
    design: SafeDesignTwoProportions,
    null_prior_a: float = 1.0,
    null_prior_b: float = 1.0,
) -> float:
    """Private helper: compute e-value for a single block using Beta-Binomial marginals.

    This exists as a module-level helper and is the computation used by
    EValueTwoProportions.update().
    """
    log_alt = marginal_loglik_two_groups(succ_a, n_a, succ_b, n_b, design)
    log_null = marginal_loglik_null_common_prob(
        succ_a, n_a, succ_b, n_b, null_prior_a, null_prior_b
    )
    # math.exp returns float; ensure we return a float for typing
    return float(math.exp(log_alt - log_null))


def _beta_binomial_marginal_likelihood(
    success: int, trials: int, a: float, b: float
) -> float:
    # betaln from scipy may be untyped; ensure we return a concrete float
    return float(betaln(a + success, b + trials - success) - betaln(a, b))


def marginal_loglik_two_groups(
    succ_a: int, n_a: int, succ_b: int, n_b: int, design: SafeDesignTwoProportions
) -> float:
    la = _beta_binomial_marginal_likelihood(succ_a, n_a, design.betaA1, design.betaA2)
    lb = _beta_binomial_marginal_likelihood(succ_b, n_b, design.betaB1, design.betaB2)
    return la + lb


def marginal_loglik_null_common_prob(
    succ_a: int, n_a: int, succ_b: int, n_b: int, a: float = 1.0, b: float = 1.0
) -> float:
    total_succ = succ_a + succ_b
    total_n = n_a + n_b
    return _beta_binomial_marginal_likelihood(total_succ, total_n, a, b)
