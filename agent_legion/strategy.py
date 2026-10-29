"""Typed strategy genome for AgentLegion agents.

A strategy is the heritable "DNA" of an agent. Every gene has an explicit
bound and mutation semantics, so evolution is reproducible and testable.
"""
from __future__ import annotations

import random
from dataclasses import dataclass, replace
from typing import Mapping

#: Gene specifications: name -> (min, max, kind). ``kind`` is ``float`` or ``int``.
GENE_SPECS: dict[str, tuple[float, float, type]] = {
    "focus": (0.0, 1.0, float),        # exploitation: step size around the incumbent
    "iteration": (1, 20, int),         # samples per act(): best-of-N search effort
    "risk_taking": (0.0, 1.0, float),  # exploration: proposal spread multiplier
}

GENE_NAMES = tuple(GENE_SPECS)


def _clamp(name: str, value: float) -> float:
    lo, hi, kind = GENE_SPECS[name]
    if value != value:  # NaN guard
        return lo
    value = max(lo, min(hi, value))
    return kind(value)


@dataclass(frozen=True)
class Strategy:
    """An agent's heritable parameters.

    Instances are validated and clamped on construction, so every Strategy
    in the system is guaranteed to lie inside :data:`GENE_SPECS` bounds.
    """

    focus: float
    iteration: int
    risk_taking: float

    def __post_init__(self) -> None:
        for name in GENE_NAMES:
            object.__setattr__(self, name, _clamp(name, getattr(self, name)))

    # -- construction -----------------------------------------------------
    @classmethod
    def random(cls, rng: "random.Random | None" = None) -> "Strategy":
        rng = rng if rng is not None else random.Random()
        lo, hi = GENE_SPECS["iteration"][:2]
        return cls(
            focus=rng.random(),
            iteration=rng.randint(int(lo), int(hi)),
            risk_taking=rng.random(),
        )

    @classmethod
    def from_mapping(cls, mapping: Mapping[str, float]) -> "Strategy":
        missing = [n for n in GENE_NAMES if n not in mapping]
        if missing:
            raise KeyError(f"strategy mapping is missing genes: {missing}")
        return cls(**{n: mapping[n] for n in GENE_NAMES})

    # -- views ------------------------------------------------------------
    def as_dict(self) -> dict[str, float]:
        return {name: getattr(self, name) for name in GENE_NAMES}

    # -- variation --------------------------------------------------------
    def mutated(self, rng: random.Random, rate: float, scale: float = 0.15) -> "Strategy":
        """Return a copy where each gene mutated independently with probability ``rate``.

        Mutation is Gaussian; the step size is ``scale`` times the gene range.
        Values are clamped back into bounds.
        """
        if not 0.0 <= rate <= 1.0:
            raise ValueError(f"mutation rate must be in [0, 1], got {rate}")
        changes: dict[str, float] = {}
        for name, value in self.as_dict().items():
            if rng.random() < rate:
                lo, hi, kind = GENE_SPECS[name]
                span = hi - lo
                delta = rng.gauss(0.0, scale * span)
                changes[name] = _clamp(name, value + delta)
        return replace(self, **changes)

    def crossover(self, other: "Strategy", rng: random.Random) -> "Strategy":
        """Uniform gene-wise crossover between two parents."""
        genes = {
            name: getattr(self, name) if rng.random() < 0.5 else getattr(other, name)
            for name in GENE_NAMES
        }
        return Strategy(**genes)

    # -- distance ---------------------------------------------------------
    def distance(self, other: "Strategy") -> float:
        """Mean absolute normalized difference across genes, in ``[0, 1]``."""
        total = 0.0
        for name in GENE_NAMES:
            lo, hi, _ = GENE_SPECS[name]
            span = hi - lo
            if span <= 0:
                continue
            total += abs(getattr(self, name) - getattr(other, name)) / span
        return total / len(GENE_NAMES)

    def __repr__(self) -> str:  # pragma: no cover - cosmetic
        return (
            f"Strategy(focus={self.focus:.3f}, "
            f"iteration={self.iteration}, risk_taking={self.risk_taking:.3f})"
        )
