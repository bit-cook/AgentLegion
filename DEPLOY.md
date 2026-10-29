# Deployment Guide

## Prerequisites

- Python 3.10 or newer
- pip

## Local Setup

```bash
git clone https://github.com/bit-cook/AgentLegion.git
cd AgentLegion
pip install .
```

AgentLegion has **zero runtime dependencies** — the core engine, the
deterministic Mock LLM backend, and even the real OpenAI-compatible client
are pure standard library. There is nothing else to install.

## Running

```bash
agentlegion run --seed 42                 # evolution demo
agentlegion experiment --trials 5         # multi-trial experiment + REPORT.md
python -m unittest discover tests -v      # test suite
python main.py                            # historical entry point
python experiment.py                      # historical entry point
```

## Configuration

Copy `.env.example` to `.env` to configure a real LLM backend, or set
`AGENTLEGION_*` environment variables directly. See the configuration table
in [README.md](README.md#️-配置) for the full list.

## Real LLM Backend

The real backend talks to any OpenAI-compatible `/chat/completions` endpoint
using `urllib`. Set `OPENAI_API_KEY` (plus optional `OPENAI_BASE_URL` and
`OPENAI_MODEL`) and run with `--backend openai`. Without a key, `auto` mode
falls back to the deterministic Mock and logs a warning; `--backend openai`
without a key exits with an error instead of faking results.

## GitHub Pages Website

The website source lives in `docs/` and is served from the `main` branch:

1. Push to `main` (the `docs/` directory is part of the repository).
2. In the repository settings, open **Pages** and set the source to
   `main` / `docs`. The site is then live at
   `https://bit-cook.github.io/AgentLegion/`.
3. The benchmark charts read `docs/assets/benchmark-data.json`. Regenerate it
   from real runs with:

   ```bash
   python scripts/generate_benchmarks.py --trials 10 --generations 40
   ```

## Troubleshooting

- **`configuration error: INITIAL_AGENTS ... cannot exceed MAX_AGENTS`** —
  the population parameters are inconsistent; check your `AGENTLEGION_*`
  variables or CLI flags.
- **`error: unknown problem`** — run `agentlegion run --help` for the list of
  registered benchmark problems.
- **Real backend returns `LLMError`** — the endpoint, key, or model is
  misconfigured, or the model reply was not valid JSON. The error message
  names the cause; nothing is silently scored as zero.
