"""Per-generation and per-run metrics."""
from __future__ import annotations

import math
import statistics
from dataclasses import dataclass, field
from typing import Any, Sequence

from .agent import Agent
from .strategy import GENE_NAMES, Strategy


def _finite_scores(agents: Sequence[Agent]) -> list[float]:
    return [a.score for a in agents if math.isfinite(a.score)]


@dataclass
class GenerationStats:
    """Statistics for one generation of the population."""

    generation: int
    population: int
    best: float
    mean: float
    median: float
    stdev: float
    diversity: float
    evaluations: int
    mean_strategy: dict[str, float] = field(default_factory=dict)

    @classmethod
    def compute(
        cls,
        generation: int,
        agents: Sequence[Agent],
        max_pairs: int = 200,
    ) -> "GenerationStats":
        scores = _finite_scores(agents)
        best = max(scores) if scores else -math.inf
        mean = statistics.fmean(scores) if scores else -math.inf
        median = statistics.median(scores) if scores else -math.inf
        stdev = statistics.pstdev(scores) if len(scores) > 1 else 0.0
        diversity = _mean_strategy_distance(agents, max_pairs)
        mean_strategy = {
            name: statistics.fmean([getattr(a.strategy, name) for a in agents])
            for name in GENE_NAMES
        } if agents else {}
        return cls(
            generation=generation,
            population=len(agents),
            best=best,
            mean=mean,
            median=median,
            stdev=stdev,
            diversity=diversity,
            evaluations=sum(a.evaluations for a in agents),
            mean_strategy=mean_strategy,
        )

    def as_dict(self) -> dict[str, Any]:
        return {
            "generation": self.generation,
            "population": self.population,
            "best": self.best,
            "mean": self.mean,
            "median": self.median,
            "stdev": self.stdev,
            "diversity": self.diversity,
            "evaluations": self.evaluations,
            "mean_strategy": dict(self.mean_strategy),
        }


def _mean_strategy_distance(agents: Sequence[Agent], max_pairs: int) -> float:
    """Mean pairwise normalized strategy distance (sampled when population is large)."""
    n = len(agents)
    if n < 2:
        return 0.0
    strategies: list[Strategy] = [a.strategy for a in agents]
    total_pairs = n * (n - 1) // 2
    if total_pairs <= max_pairs:
        pairs = (
            (i, j) for i in range(n) for j in range(i + 1, n)
        )
    else:  # deterministic sampled pairs
        step = max(1, total_pairs // max_pairs)
        pairs = []
        count = 0
        for i in range(n):
            for j in range(i + 1, n):
                if count % step == 0:
                    pairs.append((i, j))
                count += 1
    dists = [strategies[i].distance(strategies[j]) for i, j in pairs]
    return statistics.fmean(dists) if dists else 0.0


@dataclass
class RunResult:
    """The full record of one simulation run."""

    problem: str
    seed: int | None
    config: dict[str, Any]
    stats: list[GenerationStats]
    best_agent: dict[str, Any] | None
    wall_time: float
    llm_backend: str = "mock"

    # -- analysis ---------------------------------------------------------
    def convergence_generation(self, tolerance: float = 1e-9, patience: int = 5) -> int | None:
        """First generation after which the best score stops improving.

        Returns ``None`` if the best score was still improving at the end.
        """
        bests = [s.best for s in self.stats]
        if len(bests) < patience + 1:
            return None
        for i in range(len(bests) - patience):
            window = bests[i : i + patience + 1]
            if max(window) - window[0] <= tolerance:
                return i
        return None

    def summary(self) -> dict[str, Any]:
        if not self.stats:
            return {}
        first, last = self.stats[0], self.stats[-1]
        bests = [s.best for s in self.stats]
        auc = sum(bests) / len(bests)
        return {
            "problem": self.problem,
            "seed": self.seed,
            "generations": len(self.stats),
            "final_population": last.population,
            "initial_best": first.best,
            "final_best": last.best,
            "best_overall": max(bests),
            "improvement": last.best - first.best,
            "mean_auc": auc,
            "final_diversity": last.diversity,
            "convergence_generation": self.convergence_generation(),
            "total_evaluations": last.evaluations,
            "wall_time": self.wall_time,
            "llm_backend": self.llm_backend,
        }

    def series(self, key: str = "best") -> list[float]:
        return [getattr(s, key) for s in self.stats]
