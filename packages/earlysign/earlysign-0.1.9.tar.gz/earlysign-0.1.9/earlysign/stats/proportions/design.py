from dataclasses import dataclass
from typing import Dict, Optional


@dataclass
class SafeDesignTwoProportions:
    na: int
    nb: int
    alpha: float = 0.05
    betaA1: float = 1.0
    betaA2: float = 1.0
    betaB1: float = 1.0
    betaB2: float = 1.0
    nBlocksPlan: Optional[int] = None

    name: str = "safe2x2"
    description: str = "Safe two-proportions design (Beta-Binomial)"

    def max_samples(self) -> int:
        if self.nBlocksPlan is None:
            return 0
        return int(self.nBlocksPlan * (self.na + self.nb))

    def spending_function(self, t: float) -> float:
        return min(1.0, max(0.0, self.alpha * t))


def design_safe_two_proportions(
    na: int,
    nb: int,
    alpha: float = 0.05,
    hyperparameter_values: Optional[Dict[str, float]] = None,
    nBlocksPlan: Optional[int] = None,
) -> SafeDesignTwoProportions:
    if hyperparameter_values is None:
        hyperparameter_values = {}
    return SafeDesignTwoProportions(
        na=na,
        nb=nb,
        alpha=alpha,
        betaA1=hyperparameter_values.get("betaA1", 1.0),
        betaA2=hyperparameter_values.get("betaA2", 1.0),
        betaB1=hyperparameter_values.get("betaB1", 1.0),
        betaB2=hyperparameter_values.get("betaB2", 1.0),
        nBlocksPlan=nBlocksPlan,
    )
