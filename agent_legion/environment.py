"""The Environment: the evolutionary loop where agents compete and clone.

Pipeline per generation:

1. **Act** — every agent proposes solutions on the problem and updates its
   incumbent (best-so-far) score.
2. **Evaluate** — the population is ranked; generation statistics are recorded.
3. **Select** — the top ``ELITE_RATE`` survive untouched; the remaining
   reproduction slots are filled by tournament-selected parents.
4. **Reproduce** — parents either clone (asexual) or breed (crossover),
   each child inheriting its parent's incumbent point and a mutated strategy.

The best score is monotone non-decreasing: every agent's incumbent score
only ever improves, and the top scorers of each generation keep acting,
so the population maximum can never fall.
"""
from __future__ import annotations

import logging
import random
import time
from typing import Any, Iterable

from .agent import Agent
from .config import ConfigError, load_config
from .llm import MockLLM, OpenAILLM, Solver, create_llm
from .metrics import GenerationStats, RunResult
from .problems import Problem, get_problem

logger = logging.getLogger("agent_legion.environment")


class Environment:
    """A population of agents evolving on one problem."""

    def __init__(
        self,
        config: Any = None,
        problem: Problem | None = None,
        llm: "Solver | None" = None,
        seed: int | None = None,
    ):
        if config is None or isinstance(config, type):
            config = load_config()
        self.config = config
        _validate_config(config)
        self.seed = seed if seed is not None else getattr(config, "SEED", None)
        self.rng = random.Random(self.seed)
        self.problem = problem if problem is not None else get_problem(
            getattr(config, "PROBLEM", "rastrigin")
        )
        self.llm = llm if llm is not None else create_llm(config)
        self.agents: list[Agent] = [
            Agent(llm=self.llm, rng=self.rng)
            for _ in range(min(config.INITIAL_AGENTS, config.MAX_AGENTS))
        ]
        self.generation = 0
        self.best_agent: Agent | None = None
        self.best_score = -float("inf")
        self.history: list[GenerationStats] = []

    # -- the loop ---------------------------------------------------------
    def run_generation(self, verbose: bool = False) -> GenerationStats:
        # 1. Action phase
        for agent in self.agents:
            agent.act(self.problem)

        # 2. Evaluation phase
        self.agents.sort(key=lambda a: a.score, reverse=True)
        self.best_agent = self.agents[0]
        self.best_score = max(self.best_score, self.best_agent.score)
        stats = GenerationStats.compute(self.generation, self.agents)
        self.history.append(stats)

        if verbose:
            logger.info(
                "gen %d | pop %d | best %.6f | mean %.6f | diversity %.3f",
                stats.generation,
                stats.population,
                stats.best,
                stats.mean,
                stats.diversity,
            )
            print(
                f"Generation {stats.generation}: population={stats.population} "
                f"best={stats.best:.6f} mean={stats.mean:.6f} "
                f"diversity={stats.diversity:.3f}"
            )

        # 3. Selection phase
        n = len(self.agents)
        elite_count = max(1, int(n * self.config.ELITE_RATE))
        elites = self.agents[:elite_count]
        parents = list(elites)
        needed_parents = n - elite_count
        for _ in range(needed_parents):
            parents.append(self._tournament())

        # 4. Reproduction phase
        children: list[Agent] = []
        slots = self.config.MAX_AGENTS - elite_count
        while len(children) < slots:
            parent = parents[len(children) % len(parents)]
            if self.rng.random() < self.config.CROSSOVER_RATE and len(parents) > 1:
                partner = parents[self.rng.randrange(len(parents))]
                child = parent.breed(partner, self.config.MUTATION_RATE)
            else:
                child = parent.clone(self.config.MUTATION_RATE)
            children.append(child)

        self.agents = elites + children
        self.generation += 1
        return stats

    def _tournament(self) -> Agent:
        size = max(2, min(self.config.TOURNAMENT_SIZE, len(self.agents)))
        contenders = [self.agents[self.rng.randrange(len(self.agents))] for _ in range(size)]
        return max(contenders, key=lambda a: a.score)

    def run_simulation(
        self, generations: int | None = None, verbose: bool = False
    ) -> RunResult:
        generations = int(
            generations if generations is not None else self.config.GENERATIONS
        )
        start = time.perf_counter()
        for _ in range(generations):
            self.run_generation(verbose=verbose)
        wall = time.perf_counter() - start
        return RunResult(
            problem=self.problem.name,
            seed=self.seed,
            config=_config_snapshot(self.config),
            stats=list(self.history),
            best_agent=self.best_agent.describe() if self.best_agent else None,
            wall_time=wall,
            llm_backend=getattr(self.llm, "name", "mock"),
        )

    # -- convenience ------------------------------------------------------
    def best_series(self) -> list[float]:
        return [s.best for s in self.history]

    def __repr__(self) -> str:  # pragma: no cover - cosmetic
        return (
            f"<Environment problem={self.problem.name} "
            f"generation={self.generation} population={len(self.agents)} "
            f"best={self.best_score:.6f}>"
        )


def _validate_config(config: Any) -> None:
    checks = [
        ("INITIAL_AGENTS", getattr(config, "INITIAL_AGENTS", None), 1, None),
        ("MAX_AGENTS", getattr(config, "MAX_AGENTS", None), 1, None),
        ("GENERATIONS", getattr(config, "GENERATIONS", None), 1, None),
        ("MUTATION_RATE", getattr(config, "MUTATION_RATE", None), 0.0, 1.0),
        ("ELITE_RATE", getattr(config, "ELITE_RATE", None), 0.0, 1.0),
        ("CROSSOVER_RATE", getattr(config, "CROSSOVER_RATE", None), 0.0, 1.0),
        ("TOURNAMENT_SIZE", getattr(config, "TOURNAMENT_SIZE", None), 2, None),
    ]
    for name, value, lo, hi in checks:
        if value is None:
            raise ConfigError(f"config is missing {name}")
        if not isinstance(value, (int, float)) or isinstance(value, bool):
            raise ConfigError(f"{name} must be a number, got {value!r}")
        if value < lo or (hi is not None and value > hi):
            raise ConfigError(f"{name}={value} outside allowed range [{lo}, {hi}]")
    if config.INITIAL_AGENTS > config.MAX_AGENTS:
        raise ConfigError(
            f"INITIAL_AGENTS ({config.INITIAL_AGENTS}) cannot exceed "
            f"MAX_AGENTS ({config.MAX_AGENTS})"
        )


def _config_snapshot(config: Any) -> dict[str, Any]:
    keys = (
        "INITIAL_AGENTS",
        "MAX_AGENTS",
        "GENERATIONS",
        "MUTATION_RATE",
        "ELITE_RATE",
        "CROSSOVER_RATE",
        "TOURNAMENT_SIZE",
        "PROBLEM",
        "PROBLEM_DIMENSION",
        "LLM_BACKEND",
    )
    return {k: getattr(config, k, None) for k in keys}
