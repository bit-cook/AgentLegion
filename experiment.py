"""Historical entry point — runs the multi-trial experiment.

Equivalent to ``agentlegion experiment``. Bare flags are forwarded to the
experiment subcommand, so ``python experiment.py --trials 3`` works.
"""
import sys

from agent_legion.cli import main

_KNOWN_SUBCOMMANDS = {"run", "experiment"}


def _build_argv() -> list[str]:
    forwarded = sys.argv[1:]
    if forwarded and forwarded[0] in _KNOWN_SUBCOMMANDS:
        return forwarded
    return ["experiment", *forwarded]


if __name__ == "__main__":
    raise SystemExit(main(_build_argv()))
