"""The Agent: a self-cloning, competing solver.

An agent carries a heritable :class:`~agent_legion.strategy.Strategy`, an
incumbent solution (its best point so far), and a shared LLM provider. Each
generation it *acts* on the problem, and the fittest agents *clone* or
*breed* to populate the next generation.
"""
from __future__ import annotations

import random
import uuid
from typing import Sequence

from .llm import LLMError, MockLLM, Solution, Solver
from .problems import Problem
from .strategy import Strategy


class Agent:
    """A single competing solver in the population."""

    def __init__(
        self,
        strategy: Strategy | None = None,
        generation: int = 0,
        parent_id: str | None = None,
        parent_ids: Sequence[str] | None = None,
        llm: "Solver | None" = None,
        rng: random.Random | None = None,
        incumbent_x: Sequence[float] | None = None,
    ):
        self.id = uuid.uuid4().hex[:8]
        self.strategy = strategy if strategy is not None else Strategy.random(rng)
        self.generation = generation
        self.parent_id = parent_id
        self.parent_ids = tuple(parent_ids) if parent_ids else (
            (parent_id,) if parent_id else ()
        )
        self.llm = llm if llm is not None else MockLLM()
        self.rng = rng if rng is not None else random.Random()
        self.incumbent_x: list[float] | None = (
            list(incumbent_x) if incumbent_x is not None else None
        )
        self.score = -float("inf")
        self.evaluations = 0
        self.is_alive = True

    # -- behavior ---------------------------------------------------------
    def act(self, problem: Problem) -> float:
        """Propose solutions on ``problem`` and keep the best one ever found.

        Returns the agent's incumbent (best-so-far) score.
        """
        solution: Solution = self.llm.propose(
            problem, self.strategy, self.incumbent_x, self.rng
        )
        self.evaluations += solution.samples
        if self.incumbent_x is None or solution.score > self.score:
            self.incumbent_x = list(solution.x)
            self.score = solution.score
        return self.score

    # -- reproduction -----------------------------------------------------
    def clone(self, mutation_rate: float = 0.25) -> "Agent":
        """Asexual reproduction: mutated copy of this agent (same incumbent)."""
        child = Agent(
            strategy=self.strategy.mutated(self.rng, mutation_rate),
            generation=self.generation + 1,
            parent_id=self.id,
            llm=self.llm,
            rng=self.rng,
            incumbent_x=self.incumbent_x,
        )
        return child

    def breed(self, other: "Agent", mutation_rate: float = 0.25) -> "Agent":
        """Sexual reproduction: gene-wise crossover of two parents, then mutation."""
        if not isinstance(other, Agent):
            raise TypeError(f"can only breed with another Agent, got {type(other)!r}")
        child = Agent(
            strategy=self.strategy.crossover(other.strategy, self.rng).mutated(
                self.rng, mutation_rate
            ),
            generation=max(self.generation, other.generation) + 1,
            parent_id=self.id,
            parent_ids=(self.id, other.id),
            llm=self.llm,
            rng=self.rng,
            incumbent_x=self.incumbent_x if self.score >= other.score else other.incumbent_x,
        )
        return child

    # -- views ------------------------------------------------------------
    @property
    def lineage_depth(self) -> int:
        return self.generation

    def describe(self) -> dict:
        return {
            "id": self.id,
            "generation": self.generation,
            "parent_ids": list(self.parent_ids),
            "score": self.score if self.score != -float("inf") else None,
            "strategy": self.strategy.as_dict(),
            "incumbent_x": self.incumbent_x,
            "evaluations": self.evaluations,
        }

    def __repr__(self) -> str:
        score = f"{self.score:.4f}" if self.score != -float("inf") else "n/a"
        return f"<Agent {self.id} Gen{self.generation} Score={score}>"


__all__ = ["Agent", "LLMError"]
