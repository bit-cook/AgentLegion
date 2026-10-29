"""AgentLegion — self-cloning AI agents that compete for optimal solutions.

一生万物 (One becomes many): agents propose solutions, compete on real
objective functions, and the fittest clone and breed to explore the
solution space further.
"""
from .version import __version__

from .agent import Agent
from .config import Config, ConfigError, load_config
from .environment import Environment
from .llm import LLMError, MockLLM, OpenAILLM, Solution, Solver, create_llm
from .metrics import GenerationStats, RunResult
from .problems import PROBLEMS, Problem, get_problem
from .report import render_report, write_report
from .strategy import GENE_SPECS, Strategy

__all__ = [
    "__version__",
    "Agent",
    "Config",
    "ConfigError",
    "Environment",
    "GENE_SPECS",
    "GenerationStats",
    "LLMError",
    "MockLLM",
    "OpenAILLM",
    "PROBLEMS",
    "Problem",
    "RunResult",
    "Solution",
    "Solver",
    "Strategy",
    "create_llm",
    "get_problem",
    "load_config",
    "render_report",
    "write_report",
]
