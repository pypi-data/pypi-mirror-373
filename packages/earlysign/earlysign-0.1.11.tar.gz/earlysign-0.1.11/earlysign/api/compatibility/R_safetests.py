from __future__ import annotations

from typing import Dict, List, Optional
import random

# The compatibility layer depends on the repository's statistic and runner components.
from earlysign.stats.proportions.design import design_safe_two_proportions
from earlysign.stats.proportions.design import SafeDesignTwoProportions
from earlysign.stats.proportions.statistics import EValueTwoProportions


def safe_two_proportions_test(
    ya: List[int],
    yb: List[int],
    design: Optional[SafeDesignTwoProportions] = None,
    want_confidence_sequence: bool = False,
) -> Dict[str, object]:
    if design is None:
        design = design_safe_two_proportions(na=1, nb=1)
    assert len(ya) == len(yb), "ya and yb must have same number of blocks"
    # Use the repository Statistic to consume blocks and produce cumulative e-values.
    stat = EValueTwoProportions(design=design)
    e_trajectory: List[float] = []
    for t, (a_block, b_block) in enumerate(zip(ya, yb), start=1):
        stat.update(t, (a_block, b_block))
        e_trajectory.append(stat.current_value or 1.0)

    return {
        "e_value": stat.current_value or 1.0,
        "e_trajectory": e_trajectory,
        "n_blocks": len(ya),
        "design": design,
        "reject": (stat.current_value or 1.0) > 1.0 / design.alpha,
    }


def simulate_optional_stopping_two_proportions(
    design: SafeDesignTwoProportions,
    thetaA: float,
    thetaB: float,
    M: int = 1000,
    max_blocks: int = 1000,
) -> Dict[str, object]:
    stopping_times: List[int] = []
    rejected = 0
    for _ in range(M):
        stat = EValueTwoProportions(design=design)
        for t in range(1, max_blocks + 1):
            succ_a = sum(random.random() < thetaA for _ in range(design.na))
            succ_b = sum(random.random() < thetaB for _ in range(design.nb))
            stat.update(t, (succ_a, succ_b))
            if (stat.current_value or 1.0) > 1.0 / design.alpha:
                rejected += 1
                stopping_times.append(t)
                break
        else:
            stopping_times.append(max_blocks)

    return {
        "power_optimal_stop": rejected / M,
        "mean_stopping_time": sum(stopping_times) / len(stopping_times),
        "stopping_times": stopping_times,
    }


__all__ = [
    "SafeDesignTwoProportions",
    "design_safe_two_proportions",
    "safe_two_proportions_test",
    "simulate_optional_stopping_two_proportions",
]
