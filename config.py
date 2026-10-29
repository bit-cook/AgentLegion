"""Backwards-compatible shim: configuration now lives in ``agent_legion.config``.

The canonical import is ``from agent_legion import load_config`` / ``Config``;
this module keeps the historical ``from config import Config`` working when
running from a source checkout.
"""
from agent_legion.config import Config, ConfigError, load_config

__all__ = ["Config", "ConfigError", "load_config"]
