"""LLM providers: the solution proposers agents evolve around.

Two providers implement the same contract:

* :class:`MockLLM` — a deterministic, seeded simulator of a search process
  (best-of-N local search around the agent's incumbent point). Given the
  same seed and strategy it always proposes the same solutions, which makes
  experiments reproducible.
* :class:`OpenAILLM` — a real OpenAI-compatible chat-completions client built
  on the standard library only (``urllib``), so using a real model adds no
  dependencies. Solutions are parsed from JSON and validated against the
  problem's dimension and bounds.

:func:`create_llm` selects a provider from configuration and fails loud:
a missing credential never silently degrades into a fake "success".
"""
from __future__ import annotations

import json
import logging
import math
import random
import urllib.error
import urllib.request
from dataclasses import dataclass, field
from typing import Any, Callable, Protocol, Sequence

from .problems import Problem

logger = logging.getLogger("agent_legion.llm")


class Solver(Protocol):
    """The provider contract: propose a solution for one agent act."""

    name: str

    def propose(
        self,
        problem: Problem,
        strategy: Any,
        incumbent_x: Sequence[float] | None,
        rng: random.Random,
    ) -> Solution:
        ...


class LLMError(RuntimeError):
    """Raised when a provider cannot produce a valid solution."""


class ConfigError(ValueError):
    """Raised for invalid provider configuration (e.g. missing API key)."""


@dataclass(frozen=True)
class Solution:
    """A proposed point plus its evaluated score."""

    x: tuple[float, ...]
    score: float
    samples: int = 1
    source: str = "mock"


@dataclass
class MockLLM:
    """Deterministic simulated solver.

    Semantics of the strategy genes (this is the "physics" agents evolve in):

    * ``iteration``  — number of candidate points sampled per act (best-of-N).
    * ``focus``      — how tightly samples cluster around the incumbent
      (1.0 = pure local refinement, 0.0 = wide exploration).
    * ``risk_taking``— exploration spread multiplier (0 = timid, 1 = bold).
    """

    name: str = "mock"

    def propose(
        self,
        problem: Problem,
        strategy: Any,
        incumbent_x: Sequence[float] | None,
        rng: random.Random,
    ) -> Solution:
        samples = max(1, int(strategy.iteration))
        lo, hi = problem.bounds
        span = hi - lo
        if incumbent_x is None:
            base = problem.random_point(rng)
        else:
            base = list(incumbent_x)

        # focus tightens the step; risk_taking widens it.
        spread = span * (0.02 + 0.5 * float(strategy.risk_taking)) * (
            1.0 - 0.75 * float(strategy.focus)
        )
        spread = max(spread, span * 1e-4)

        best_x: list[float] | None = None
        best_score = -math.inf
        for _ in range(samples):
            candidate = [
                min(max(v + rng.gauss(0.0, spread), lo), hi) for v in base
            ]
            score = problem.evaluate(candidate)
            if score > best_score:
                best_x, best_score = candidate, score
        assert best_x is not None
        return Solution(x=tuple(best_x), score=best_score, samples=samples, source=self.name)


_OPENAI_SYSTEM_PROMPT = (
    "You are a solution proposer for a numerical optimization problem. "
    "Reply with ONLY a JSON object of the form {\"x\": [..]} containing "
    "exactly the requested number of finite floats inside the given bounds."
)


@dataclass
class OpenAILLM:
    """Real OpenAI-compatible chat-completions client (stdlib only).

    Parameters
    ----------
    transport:
        Injectable ``callable(url, payload, headers) -> dict`` used for tests.
        Defaults to a real ``urllib`` POST.
    """

    api_key: str
    model: str = "gpt-4o-mini"
    base_url: str = "https://api.openai.com/v1"
    timeout: float = 30.0
    max_samples: int = 3
    name: str = "openai"
    transport: Callable[[str, dict, dict], dict] | None = field(default=None, repr=False)

    def propose(
        self,
        problem: Problem,
        strategy: Any,
        incumbent_x: Sequence[float] | None,
        rng: random.Random,
    ) -> Solution:
        samples = max(1, min(int(strategy.iteration), int(self.max_samples)))
        best: Solution | None = None
        for _ in range(samples):
            candidate = self._propose_once(problem, strategy, incumbent_x, rng)
            if best is None or candidate.score > best.score:
                best = candidate
        assert best is not None
        return best

    # -- internals --------------------------------------------------------
    def _propose_once(
        self,
        problem: Problem,
        strategy: Any,
        incumbent_x: Sequence[float] | None,
        rng: random.Random,
    ) -> Solution:
        payload = self._build_payload(problem, strategy, incumbent_x)
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
        }
        url = self.base_url.rstrip("/") + "/chat/completions"
        try:
            data = self._post(url, payload, headers)
            content = data["choices"][0]["message"]["content"]
            x = self._parse_solution(content, problem)
        except (LLMError, KeyError, IndexError, TypeError) as exc:
            raise LLMError(f"OpenAI provider could not produce a valid solution: {exc}") from exc
        except urllib.error.URLError as exc:
            raise LLMError(f"OpenAI request failed: {exc}") from exc
        return Solution(x=tuple(x), score=problem.evaluate(x), samples=1, source=self.name)

    def _build_payload(
        self,
        problem: Problem,
        strategy: Any,
        incumbent_x: Sequence[float] | None,
    ) -> dict:
        lo, hi = problem.bounds
        incumbent = (
            f"Best point found so far: {list(incumbent_x)} "
            f"(score {problem.evaluate(incumbent_x):.6f})."
            if incumbent_x is not None
            else "No incumbent yet."
        )
        user = (
            f"Problem: {problem.name} in {problem.dimension} dimensions. "
            f"Bounds: every coordinate must be within [{lo}, {hi}]. "
            f"Maximize the objective. {incumbent} "
            f"Search style: focus={strategy.focus:.3f}, "
            f"risk_taking={strategy.risk_taking:.3f}."
        )
        return {
            "model": self.model,
            "messages": [
                {"role": "system", "content": _OPENAI_SYSTEM_PROMPT},
                {"role": "user", "content": user},
            ],
            "temperature": 0.7,
            "max_tokens": 256,
        }

    def _post(self, url: str, payload: dict, headers: dict) -> dict:
        if self.transport is not None:
            return self.transport(url, payload, headers)
        request = urllib.request.Request(
            url,
            data=json.dumps(payload).encode("utf-8"),
            headers=headers,
            method="POST",
        )
        with urllib.request.urlopen(request, timeout=self.timeout) as response:
            return json.loads(response.read().decode("utf-8"))

    @staticmethod
    def _parse_solution(content: str, problem: Problem) -> list[float]:
        text = (content or "").strip()
        if text.startswith("```"):  # strip markdown fences some models add
            text = text.strip("`")
            if text.lower().startswith("json"):
                text = text[4:]
        start, end = text.find("{"), text.rfind("}")
        if start == -1 or end == -1 or end <= start:
            raise LLMError(f"no JSON object in model reply: {content!r:.200}")
        try:
            obj = json.loads(text[start : end + 1])
            raw = obj["x"]
        except (json.JSONDecodeError, KeyError) as exc:
            raise LLMError(f"malformed model reply: {exc}") from exc
        if not isinstance(raw, (list, tuple)):
            raise LLMError(f"'x' must be a list, got {type(raw).__name__}")
        if len(raw) != problem.dimension:
            raise LLMError(
                f"expected {problem.dimension} coordinates, got {len(raw)}"
            )
        try:
            x = [float(v) for v in raw]
        except (TypeError, ValueError) as exc:
            raise LLMError(f"non-numeric coordinate: {exc}") from exc
        if not all(math.isfinite(v) for v in x):
            raise LLMError("non-finite coordinate in solution")
        return problem.clip(x)


def create_llm(config: Any) -> MockLLM | OpenAILLM:
    """Build the provider selected by ``config.LLM_BACKEND``.

    * ``"mock"``  — always :class:`MockLLM`.
    * ``"openai"``— :class:`OpenAILLM`; raises :class:`ConfigError` when no
      API key is configured (fail loud, never a silent fake).
    * ``"auto"``  — :class:`OpenAILLM` when a key is present, otherwise
      :class:`MockLLM` with a loud warning.
    """
    backend = str(getattr(config, "LLM_BACKEND", "auto")).strip().lower()
    api_key = str(getattr(config, "OPENAI_API_KEY", "") or "")
    if backend == "mock":
        return MockLLM()
    if backend == "openai":
        if not api_key:
            raise ConfigError(
                "LLM_BACKEND='openai' requires OPENAI_API_KEY "
                "(set the env var or use LLM_BACKEND='auto'/'mock')"
            )
        return OpenAILLM(
            api_key=api_key,
            model=str(getattr(config, "OPENAI_MODEL", "gpt-4o-mini")),
            base_url=str(getattr(config, "OPENAI_BASE_URL", "https://api.openai.com/v1")),
            timeout=float(getattr(config, "LLM_TIMEOUT", 30.0)),
            max_samples=int(getattr(config, "LLM_MAX_SAMPLES", 3)),
        )
    if backend == "auto":
        if api_key:
            logger.info("OPENAI_API_KEY detected — using the real OpenAI provider")
            return OpenAILLM(
                api_key=api_key,
                model=str(getattr(config, "OPENAI_MODEL", "gpt-4o-mini")),
                base_url=str(getattr(config, "OPENAI_BASE_URL", "https://api.openai.com/v1")),
                timeout=float(getattr(config, "LLM_TIMEOUT", 30.0)),
                max_samples=int(getattr(config, "LLM_MAX_SAMPLES", 3)),
            )
        logger.warning(
            "no OPENAI_API_KEY set — falling back to the deterministic MockLLM "
            "(set LLM_BACKEND=openai with a key to use a real model)"
        )
        return MockLLM()
    raise ConfigError(
        f"unknown LLM_BACKEND {backend!r}; expected 'auto', 'mock' or 'openai'"
    )
