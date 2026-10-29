"""Configuration: every knob here is actually used by the engine.

Values come from defaults, overridden by ``AGENTLEGION_*`` environment
variables (plus the standard ``OPENAI_*`` variables for the real LLM
backend), overridden by explicit keyword arguments.
"""
from __future__ import annotations

import os
from dataclasses import dataclass, fields
from typing import Any, Mapping

__all__ = ["Config", "ConfigError", "load_config"]


class ConfigError(ValueError):
    """Invalid configuration value."""


def _get_env(env: Mapping[str, str] | None, key: str) -> str | None:
    env = env if env is not None else os.environ
    return env.get(key)


def _env_int(env, key: str, default: int) -> int:
    raw = _get_env(env, key)
    if raw is None or raw == "":
        return default
    try:
        return int(raw)
    except ValueError as exc:
        raise ConfigError(f"{key} must be an integer, got {raw!r}") from exc


def _env_float(env, key: str, default: float) -> float:
    raw = _get_env(env, key)
    if raw is None or raw == "":
        return default
    try:
        return float(raw)
    except ValueError as exc:
        raise ConfigError(f"{key} must be a number, got {raw!r}") from exc


@dataclass
class Config:
    """Runtime configuration for a simulation."""

    # population / evolution
    INITIAL_AGENTS: int = 5
    MAX_AGENTS: int = 50
    GENERATIONS: int = 20
    MUTATION_RATE: float = 0.25
    ELITE_RATE: float = 0.1
    CROSSOVER_RATE: float = 0.5
    TOURNAMENT_SIZE: int = 3

    # problem
    PROBLEM: str = "rastrigin"
    PROBLEM_DIMENSION: int = 2

    # reproducibility
    SEED: int | None = None

    # LLM backend: "auto" (default), "mock" or "openai"
    LLM_BACKEND: str = "auto"
    OPENAI_API_KEY: str = ""
    OPENAI_BASE_URL: str = "https://api.openai.com/v1"
    OPENAI_MODEL: str = "gpt-4o-mini"
    LLM_MAX_SAMPLES: int = 3
    LLM_TIMEOUT: float = 30.0

    @property
    def USE_MOCK_LLM(self) -> bool:
        """True when the effective backend is the deterministic mock."""
        return self.LLM_BACKEND.strip().lower() == "mock" or (
            self.LLM_BACKEND.strip().lower() == "auto" and not self.OPENAI_API_KEY
        )

    def replace(self, **overrides: Any) -> "Config":
        unknown = set(overrides) - {f.name for f in fields(self)}
        if unknown:
            raise ConfigError(f"unknown config keys: {sorted(unknown)}")
        values = {f.name: getattr(self, f.name) for f in fields(self)}
        values.update(overrides)
        return Config(**values)

    def as_dict(self) -> dict[str, Any]:
        data = {f.name: getattr(self, f.name) for f in fields(self)}
        data["USE_MOCK_LLM"] = self.USE_MOCK_LLM
        if data["OPENAI_API_KEY"]:
            data["OPENAI_API_KEY"] = "***"  # never leak secrets into reports
        return data


def load_config(env: Mapping[str, str] | None = None, **overrides: Any) -> Config:
    """Build a :class:`Config` from environment variables plus overrides."""
    env = env if env is not None else os.environ

    def pick(name: str, default: Any) -> Any:
        return overrides.pop(name, default)

    config = Config(
        INITIAL_AGENTS=_env_int(env, "AGENTLEGION_INITIAL_AGENTS", 5)
        if "INITIAL_AGENTS" not in overrides
        else overrides.pop("INITIAL_AGENTS"),
        MAX_AGENTS=_env_int(env, "AGENTLEGION_MAX_AGENTS", 50)
        if "MAX_AGENTS" not in overrides
        else overrides.pop("MAX_AGENTS"),
        GENERATIONS=_env_int(env, "AGENTLEGION_GENERATIONS", 20)
        if "GENERATIONS" not in overrides
        else overrides.pop("GENERATIONS"),
        MUTATION_RATE=_env_float(env, "AGENTLEGION_MUTATION_RATE", 0.25)
        if "MUTATION_RATE" not in overrides
        else overrides.pop("MUTATION_RATE"),
        ELITE_RATE=_env_float(env, "AGENTLEGION_ELITE_RATE", 0.1)
        if "ELITE_RATE" not in overrides
        else overrides.pop("ELITE_RATE"),
        CROSSOVER_RATE=_env_float(env, "AGENTLEGION_CROSSOVER_RATE", 0.5)
        if "CROSSOVER_RATE" not in overrides
        else overrides.pop("CROSSOVER_RATE"),
        TOURNAMENT_SIZE=_env_int(env, "AGENTLEGION_TOURNAMENT_SIZE", 3)
        if "TOURNAMENT_SIZE" not in overrides
        else overrides.pop("TOURNAMENT_SIZE"),
        PROBLEM=pick("PROBLEM", _get_env(env, "AGENTLEGION_PROBLEM") or "rastrigin"),
        PROBLEM_DIMENSION=_env_int(env, "AGENTLEGION_PROBLEM_DIMENSION", 2)
        if "PROBLEM_DIMENSION" not in overrides
        else overrides.pop("PROBLEM_DIMENSION"),
        SEED=pick("SEED", _env_int(env, "AGENTLEGION_SEED", -1) or None),
        LLM_BACKEND=pick("LLM_BACKEND", _get_env(env, "AGENTLEGION_LLM_BACKEND") or "auto"),
        OPENAI_API_KEY=pick("OPENAI_API_KEY", _get_env(env, "OPENAI_API_KEY") or ""),
        OPENAI_BASE_URL=pick(
            "OPENAI_BASE_URL",
            _get_env(env, "OPENAI_BASE_URL") or "https://api.openai.com/v1",
        ),
        OPENAI_MODEL=pick("OPENAI_MODEL", _get_env(env, "OPENAI_MODEL") or "gpt-4o-mini"),
        LLM_MAX_SAMPLES=_env_int(env, "AGENTLEGION_LLM_MAX_SAMPLES", 3)
        if "LLM_MAX_SAMPLES" not in overrides
        else overrides.pop("LLM_MAX_SAMPLES"),
        LLM_TIMEOUT=_env_float(env, "AGENTLEGION_LLM_TIMEOUT", 30.0)
        if "LLM_TIMEOUT" not in overrides
        else overrides.pop("LLM_TIMEOUT"),
    )
    if overrides:
        raise ConfigError(f"unknown config keys: {sorted(overrides)}")
    return config
