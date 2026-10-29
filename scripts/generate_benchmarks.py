#!/usr/bin/env python3
"""Regenerate the benchmark data embedded in the GitHub Pages website.

Runs the real evolution engine across every registered problem and writes
aggregated results to ``docs/assets/benchmark-data.json``. The website's
charts are drawn from this file, so every number on the site comes from an
actual recorded run.

Usage:
    python scripts/generate_benchmarks.py [--trials 10] [--generations 40]
"""
from __future__ import annotations

import argparse
import json
import statistics
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

from agent_legion.config import load_config  # noqa: E402
from agent_legion.environment import Environment  # noqa: E402
from agent_legion.problems import PROBLEMS  # noqa: E402


def run_trials(problem: str, trials: int, generations: int, seed_base: int) -> dict:
    runs = []
    for trial in range(trials):
        config = load_config({}).replace(
            INITIAL_AGENTS=5,
            MAX_AGENTS=50,
            GENERATIONS=generations,
            SEED=seed_base + trial,
            PROBLEM=problem,
            LLM_BACKEND="mock",
        )
        result = Environment(config).run_simulation()
        runs.append(
            {
                "seed": seed_base + trial,
                "best": [s.best for s in result.stats],
                "mean": [s.mean for s in result.stats],
                "diversity": [s.diversity for s in result.stats],
                "focus": [s.mean_strategy["focus"] for s in result.stats],
                "iteration": [s.mean_strategy["iteration"] for s in result.stats],
                "risk_taking": [s.mean_strategy["risk_taking"] for s in result.stats],
                "summary": result.summary(),
            }
        )

    def mean_series(key: str) -> list[float]:
        return [
            statistics.fmean(run[key][i] for run in runs)
            for i in range(generations)
        ]

    finals = [run["summary"]["final_best"] for run in runs]
    converged = [
        run["summary"]["convergence_generation"]
        for run in runs
        if run["summary"]["convergence_generation"] is not None
    ]
    return {
        "trials": trials,
        "generations": generations,
        "seed_base": seed_base,
        "mean_best": mean_series("best"),
        "mean_mean": mean_series("mean"),
        "mean_diversity": mean_series("diversity"),
        "mean_focus": mean_series("focus"),
        "mean_iteration": mean_series("iteration"),
        "mean_risk_taking": mean_series("risk_taking"),
        "final_best": {
            "min": min(finals),
            "max": max(finals),
            "mean": statistics.fmean(finals),
            "stdev": statistics.pstdev(finals) if len(finals) > 1 else 0.0,
        },
        "convergence": {
            "converged_trials": len(converged),
            "mean_generation": statistics.fmean(converged) if converged else None,
        },
        "runs": runs,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--trials", type=int, default=10)
    parser.add_argument("--generations", type=int, default=40)
    parser.add_argument("--seed-base", type=int, default=1000)
    parser.add_argument(
        "--output",
        default=str(REPO_ROOT / "docs" / "assets" / "benchmark-data.json"),
    )
    args = parser.parse_args()

    payload = {
        "meta": {
            "trials": args.trials,
            "generations": args.generations,
            "seed_base": args.seed_base,
            "population": {"initial": 5, "max": 50},
            "llm_backend": "mock (deterministic)",
        },
        "problems": {},
    }
    for name in sorted(PROBLEMS):
        print(f"benchmarking {name}: {args.trials} trials x {args.generations} generations...")
        payload["problems"][name] = run_trials(
            name, args.trials, args.generations, args.seed_base
        )

    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(f"wrote {output} ({output.stat().st_size} bytes)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
