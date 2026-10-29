"""Benchmark problems: real objective functions agents compete on.

Every problem is a *maximization* problem over a bounded box; the optimum
value is always ``0.0`` and all other points score strictly below it. Agents
propose candidate points, the problem evaluates them, and evolution selects
the proposers. This makes fitness meaningful and measurable instead of noise.
"""
from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Callable, Iterable, Sequence


@dataclass(frozen=True)
class Problem:
    """A black-box maximization problem ``f(x) -> float`` over a box."""

    name: str
    dimension: int
    bounds: tuple[float, float]

    def evaluate(self, x: Sequence[float]) -> float:
        raise NotImplementedError

    def random_point(self, rng) -> list[float]:
        lo, hi = self.bounds
        return [rng.uniform(lo, hi) for _ in range(self.dimension)]

    def clip(self, x: Iterable[float]) -> list[float]:
        lo, hi = self.bounds
        return [min(max(float(v), lo), hi) for v in x]


class SphereProblem(Problem):
    """Unimodal bowl: ``f(x) = -sum(x_i^2)``. Optimum 0.0 at the origin."""

    def __init__(self, dimension: int = 2):
        super().__init__(name="sphere", dimension=dimension, bounds=(-5.12, 5.12))

    def evaluate(self, x: Sequence[float]) -> float:
        if len(x) != self.dimension:
            raise ValueError(f"expected {self.dimension} values, got {len(x)}")
        return -sum(float(v) * float(v) for v in x)


class RastriginProblem(Problem):
    """Highly multimodal: ``f(x) = -(10n + sum(x_i^2 - 10 cos(2 pi x_i)))``.

    Rewards exploration (risk_taking) because greedy local search gets
    trapped in the many local optima. Optimum 0.0 at the origin.
    """

    def __init__(self, dimension: int = 2):
        super().__init__(name="rastrigin", dimension=dimension, bounds=(-5.12, 5.12))

    def evaluate(self, x: Sequence[float]) -> float:
        if len(x) != self.dimension:
            raise ValueError(f"expected {self.dimension} values, got {len(x)}")
        total = 10.0 * self.dimension
        for v in x:
            v = float(v)
            total += v * v - 10.0 * math.cos(2.0 * math.pi * v)
        return -total


class RosenbrockProblem(Problem):
    """Curved banana valley: ``f(x) = -sum(100 (x_{i+1} - x_i^2)^2 + (1 - x_i)^2)``.

    Optimum 0.0 at the all-ones vector. The narrow valley punishes careless
    exploration. Optimum 0.0.
    """

    def __init__(self, dimension: int = 2):
        super().__init__(name="rosenbrock", dimension=dimension, bounds=(-2.048, 2.048))

    def evaluate(self, x: Sequence[float]) -> float:
        if len(x) != self.dimension:
            raise ValueError(f"expected {self.dimension} values, got {len(x)}")
        total = 0.0
        for i in range(self.dimension - 1):
            a = float(x[i + 1]) - float(x[i]) ** 2
            b = 1.0 - float(x[i])
            total += 100.0 * a * a + b * b
        return -total


PROBLEMS: dict[str, Callable[[int], Problem]] = {
    "sphere": SphereProblem,
    "rastrigin": RastriginProblem,
    "rosenbrock": RosenbrockProblem,
}


def get_problem(name: str, dimension: int = 2) -> Problem:
    """Instantiate a registered problem by name (case-insensitive)."""
    key = str(name).strip().lower()
    if key not in PROBLEMS:
        raise ValueError(
            f"unknown problem {name!r}; available: {', '.join(sorted(PROBLEMS))}"
        )
    return PROBLEMS[key](dimension)
