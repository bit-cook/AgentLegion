"""Command-line interface: ``agentlegion run`` / ``agentlegion experiment``.

The historical entry points keep working: ``python main.py`` runs the demo
and ``python experiment.py`` runs the multi-trial experiment.
"""
from __future__ import annotations

import argparse
import csv
import json
import logging
import sys
from typing import Any, Sequence

from .version import __version__
from .config import ConfigError, load_config
from .environment import Environment
from .metrics import RunResult
from .problems import PROBLEMS, get_problem
from .report import render_report

logger = logging.getLogger("agent_legion")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="agentlegion",
        description=(
            "Self-cloning AI agents that compete for optimal solutions. "
            "一生万物 — one becomes many."
        ),
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    parser.add_argument(
        "--log-level",
        default="WARNING",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        help="logging verbosity (default: WARNING)",
    )
    sub = parser.add_subparsers(dest="command")

    run = sub.add_parser("run", help="run a single evolution demo (default command)")
    _add_common(run)
    run.add_argument("--quiet", action="store_true", help="suppress per-generation output")
    exp = sub.add_parser("experiment", help="run multiple trials and write a report")
    _add_common(exp)
    exp.add_argument("--trials", type=int, default=5, help="number of independent runs")
    exp.add_argument("--csv", default="experiment_results.csv", help="CSV output path")
    exp.add_argument("--report", default="REPORT.md", help="markdown report output path")
    exp.add_argument("--json", default=None, help="optional JSON output path")
    exp.add_argument("--quiet", action="store_true", help="suppress per-generation output")

    return parser


def _add_common(p: argparse.ArgumentParser) -> None:
    p.add_argument("--seed", type=int, default=None, help="RNG seed for reproducibility")
    p.add_argument("--generations", type=int, default=None, help="number of generations")
    p.add_argument("--initial", type=int, default=None, help="initial population size")
    p.add_argument("--population", type=int, default=None, help="maximum population size")
    p.add_argument("--mutation-rate", type=float, default=None, help="per-gene mutation rate")
    p.add_argument("--crossover-rate", type=float, default=None, help="crossover probability")
    p.add_argument("--elite-rate", type=float, default=None, help="elite survival fraction")
    p.add_argument(
        "--problem",
        default=None,
        choices=sorted(PROBLEMS),
        help="benchmark problem (default: rastrigin)",
    )
    p.add_argument(
        "--dimension", type=int, default=None, help="problem dimension (default: 2)"
    )
    p.add_argument(
        "--backend",
        default=None,
        choices=["auto", "mock", "openai"],
        help="LLM backend (default: auto — real API when a key is set)",
    )
    p.add_argument(
        "--log-level",
        default=None,
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        help="logging verbosity (default: WARNING)",
    )


def _config_from_args(args: argparse.Namespace):
    overrides = {
        key: value
        for key, value in {
            "SEED": args.seed,
            "GENERATIONS": args.generations,
            "INITIAL_AGENTS": args.initial,
            "MAX_AGENTS": args.population,
            "MUTATION_RATE": args.mutation_rate,
            "CROSSOVER_RATE": args.crossover_rate,
            "ELITE_RATE": args.elite_rate,
            "PROBLEM": args.problem,
            "PROBLEM_DIMENSION": args.dimension,
            "LLM_BACKEND": args.backend,
        }.items()
        if value is not None
    }
    return load_config(**overrides)


def cmd_run(args: argparse.Namespace) -> int:
    config = _config_from_args(args)
    verbose = not args.quiet
    if verbose:
        print("Initializing AgentLegion...")
        print(
            f"Configuration: problem={config.PROBLEM} "
            f"agents={config.INITIAL_AGENTS}->{config.MAX_AGENTS} "
            f"generations={config.GENERATIONS} seed={config.SEED}"
        )
    env = Environment(config)
    result = env.run_simulation(verbose=verbose)
    s = result.summary()
    if verbose:
        print("\n=== Simulation Complete ===")
        print(f"Final Best Agent: {result.best_agent}")
        print(f"Best score: {s['final_best']:.6f} (was {s['initial_best']:.6f})")
        print(f"Total time: {s['wall_time']:.4f}s")
    else:
        print(json.dumps(s, default=str))
    return 0


def cmd_experiment(args: argparse.Namespace) -> int:
    config = _config_from_args(args)
    trials = max(1, args.trials)
    verbose = not args.quiet
    base_seed = config.SEED if config.SEED is not None else 0
    rows: list[dict[str, Any]] = []
    results: list[RunResult] = []
    print(f"Running {trials} experimental trials on '{config.PROBLEM}'...")
    for trial in range(trials):
        seed = base_seed + trial
        env = Environment(config.replace(SEED=seed))
        result = env.run_simulation(verbose=False)
        results.append(result)
        if verbose:
            print(
                f"  trial {trial + 1}/{trials} (seed {seed}): "
                f"best {result.summary()['final_best']:.6f} "
                f"after {len(result.stats)} generations"
            )
        for stats in result.stats:
            rows.append(
                {
                    "Trial": trial + 1,
                    "Generation": stats.generation,
                    "Best_Score": f"{stats.best:.6f}",
                    "Mean_Score": f"{stats.mean:.6f}",
                    "Population": stats.population,
                }
            )

    with open(args.csv, "w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=["Trial", "Generation", "Best_Score", "Mean_Score", "Population"],
        )
        writer.writeheader()
        writer.writerows(rows)

    summary = {
        "trials": trials,
        "problem": config.PROBLEM,
        "seed_base": base_seed,
        "final_best": {
            "min": min(r.summary()["final_best"] for r in results),
            "max": max(r.summary()["final_best"] for r in results),
            "mean": sum(r.summary()["final_best"] for r in results) / trials,
        },
        "converged_trials": sum(
            1 for r in results if r.summary()["convergence_generation"] is not None
        ),
        "wall_time_total": sum(r.wall_time for r in results),
    }
    findings = [
        f"Across {trials} seeded trials, the final best score ranged from "
        f"{summary['final_best']['min']:.6f} to {summary['final_best']['max']:.6f} "
        f"(mean {summary['final_best']['mean']:.6f}).",
        f"{summary['converged_trials']}/{trials} trials reached a stable best score "
        "before the generation budget ran out.",
        "Every trial is reproducible from its seed; re-running with the same "
        "seed reproduces the same numbers exactly.",
    ]
    report_text = render_report(results[0], extra_findings=findings)
    with open(args.report, "w", encoding="utf-8") as handle:
        handle.write(report_text)
    if args.json:
        with open(args.json, "w", encoding="utf-8") as handle:
            json.dump(
                {
                    "summary": summary,
                    "runs": [
                        {"seed": r.seed, "summary": r.summary(), "stats": [s.as_dict() for s in r.stats]}
                        for r in results
                    ],
                },
                handle,
                indent=2,
                default=str,
            )
    print(f"\nExperiment complete. Results saved to '{args.csv}' and '{args.report}'.")
    print(
        f"Final best across trials: min={summary['final_best']['min']:.6f} "
        f"mean={summary['final_best']['mean']:.6f} max={summary['final_best']['max']:.6f}"
    )
    return 0


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    argv = list(sys.argv[1:] if argv is None else argv)
    # Historical UX: `python main.py [--flags]` runs the demo. Only top-level
    # help/version flags may appear without an explicit subcommand.
    if not argv or (
        argv[0].startswith("-") and argv[0] not in ("-h", "--help", "--version")
    ):
        argv = ["run", *argv]
    args = parser.parse_args(argv)
    if getattr(args, "log_level", None) is None:
        args.log_level = "WARNING"
    logging.basicConfig(
        level=getattr(logging, args.log_level),
        format="%(levelname)s %(name)s: %(message)s",
    )
    command = args.command or "run"
    try:
        if command == "run":
            return cmd_run(args)
        if command == "experiment":
            return cmd_experiment(args)
        parser.error(f"unknown command {command!r}")
        return 2
    except ConfigError as exc:
        print(f"configuration error: {exc}", file=sys.stderr)
        return 2
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
