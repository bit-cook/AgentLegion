# AgentLegion

**Self-cloning AI agents that compete for optimal solutions. One becomes many.**

[![CI](https://github.com/bit-cook/AgentLegion/actions/workflows/ci.yml/badge.svg)](https://github.com/bit-cook/AgentLegion/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/downloads/)
[![Dependencies](https://img.shields.io/badge/dependencies-0-brightgreen.svg)](pyproject.toml)
[![Website](https://img.shields.io/badge/website-live-8b5cf6.svg)](https://bit-cook.github.io/AgentLegion/)

[中文文档](README.md) · [Website](https://bit-cook.github.io/AgentLegion/) · [Experiment Report](REPORT.md)

## Overview

AgentLegion is a framework for autonomous AI agents that propose solutions on
**real benchmark optimization problems**, compete for survival, and propagate
winning strategies through **self-cloning and crossover**. It replaces
"random numbers pretending to be intelligence" with reproducible experiments:
every run is seeded, recorded, and auditable.

The core idea: **evolve how agents search, instead of hand-coding the search.**

## Features

- **Real evolution engine** — elitism + tournament selection + clone/crossover
  + per-gene Gaussian mutation, with measurable improvement on real objective
  functions (see [REPORT.md](REPORT.md)).
- **Fully reproducible** — all randomness flows through an injectable seeded
  RNG; the same seed reproduces the same run exactly.
- **Two LLM backends** — a zero-dependency deterministic Mock by default, and
  a real OpenAI-compatible API client (also stdlib-only) when
  `OPENAI_API_KEY` is set. No silent fakery: a missing key logs an explicit
  warning, and `--backend openai` without a key fails loudly.
- **Typed strategy genes** — `focus / iteration / risk_taking` with explicit
  bounds and semantics; mutation, crossover and diversity metrics are tested.
- **Real metrics** — per-generation best/mean/median/stdev, population
  diversity in strategy space, total evaluations, convergence detection.
- **121 tests** — invariants, determinism, CLI smoke, report/data consistency.
- **Zero runtime dependencies** — `pip install .` is all you need, Python ≥ 3.10.

## Quickstart

```bash
git clone https://github.com/bit-cook/AgentLegion.git
cd AgentLegion
pip install .

agentlegion run --seed 42      # or: python main.py --seed 42
```

The core in thirty lines:

```python
from agent_legion import Environment, load_config

config = load_config(SEED=42, GENERATIONS=20, PROBLEM="rastrigin")
env = Environment(config)
result = env.run_simulation()

print(result.summary()["final_best"])   # evolves from ~-10.47 to ~-0.0001
```

Run multi-trial experiments and generate the report (REPORT.md is rendered
from real run data, never hand-written):

```bash
agentlegion experiment --trials 5 --generations 20 --seed 42
```

Run the tests:

```bash
python -m unittest discover tests -v
```

## How It Works

Each generation has four phases: **Act** (every agent samples candidate
solutions), **Evaluate** (rank by incumbent score), **Select** (elites +
tournament parents), **Reproduce** (clone or crossover with mutation).

The strategy genes define *how* an agent searches — that is what evolves:

| Gene | Range | Meaning |
|---|---|---|
| `iteration` | 1 – 20 | candidates sampled per act (best-of-N effort) |
| `focus` | 0.0 – 1.0 | how tightly samples cluster around the incumbent |
| `risk_taking` | 0.0 – 1.0 | exploration spread multiplier |

**Benchmark problems** (all maximization, optimum 0.0): `sphere` (unimodal),
`rastrigin` (dense multimodal), `rosenbrock` (curved valley).

## Using a Real LLM

The default backend is the deterministic Mock (offline, reproducible). To use
a real OpenAI-compatible model:

```bash
export OPENAI_API_KEY=sk-...
export OPENAI_BASE_URL=https://api.openai.com/v1   # any compatible endpoint
export OPENAI_MODEL=gpt-4o-mini
agentlegion run --backend openai
```

Backend selection (`LLM_BACKEND` / `--backend`):

- `auto` (default): real API when a key is present, otherwise Mock with an
  explicit warning.
- `mock`: always the deterministic Mock.
- `openai`: force the real API — **a missing key is a hard error**, never a
  silent downgrade.

## Configuration

Every knob below is actually used by the engine. Override with
`AGENTLEGION_*` environment variables or CLI flags:

`AGENTLEGION_INITIAL_AGENTS` (5), `AGENTLEGION_MAX_AGENTS` (50),
`AGENTLEGION_GENERATIONS` (20), `AGENTLEGION_MUTATION_RATE` (0.25),
`AGENTLEGION_ELITE_RATE` (0.1), `AGENTLEGION_CROSSOVER_RATE` (0.5),
`AGENTLEGION_TOURNAMENT_SIZE` (3), `AGENTLEGION_PROBLEM` (rastrigin),
`AGENTLEGION_PROBLEM_DIMENSION` (2), `AGENTLEGION_SEED` (random),
`AGENTLEGION_LLM_BACKEND` (auto).

## Project Layout

```
agent_legion/   core package (zero dependencies)
  agent.py        act / clone / breed
  strategy.py     typed genes: bounds, mutation, crossover, distance
  environment.py  the evolution loop
  problems.py     benchmark objective functions
  llm.py          Mock (deterministic) + OpenAI-compatible (urllib) backends
  metrics.py      per-generation statistics and convergence detection
  report.py       report rendering from real run data
  config.py       configuration loading and validation
  cli.py          the agentlegion command line
tests/           121 unit tests
scripts/          regenerate the website benchmark data
docs/             the official website (GitHub Pages)
main.py, experiment.py   historical entry points (backwards compatible)
```

## Website

**https://bit-cook.github.io/AgentLegion/** — live evolution demo (the full
algorithm runs in your browser), real benchmark curves, and architecture notes.

## License

[MIT License](LICENSE)
