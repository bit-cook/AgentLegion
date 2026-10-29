"""Historical entry point — runs the evolution demo.

Equivalent to ``agentlegion run`` (or ``python -m agent_legion.cli run``).
"""
from agent_legion.cli import main

if __name__ == "__main__":
    raise SystemExit(main())
