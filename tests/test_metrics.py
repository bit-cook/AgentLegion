import math
import random
import unittest

from agent_legion.agent import Agent
from agent_legion.config import ConfigError, load_config
from agent_legion.llm import MockLLM
from agent_legion.metrics import GenerationStats, RunResult
from agent_legion.strategy import Strategy


def make_agent(score, focus=0.5, iteration=10, risk=0.5):
    agent = Agent(strategy=Strategy(focus, iteration, risk), llm=MockLLM())
    agent.score = score
    return agent


class TestGenerationStats(unittest.TestCase):
    def test_compute_statistics(self):
        agents = [make_agent(s) for s in (1.0, 2.0, 3.0, 4.0)]
        stats = GenerationStats.compute(0, agents)
        self.assertEqual(stats.generation, 0)
        self.assertEqual(stats.population, 4)
        self.assertEqual(stats.best, 4.0)
        self.assertAlmostEqual(stats.mean, 2.5)
        self.assertAlmostEqual(stats.median, 2.5)
        self.assertAlmostEqual(stats.stdev, 1.118033988749895)

    def test_single_agent_stdev_is_zero(self):
        stats = GenerationStats.compute(0, [make_agent(1.0)])
        self.assertEqual(stats.stdev, 0.0)

    def test_empty_population(self):
        stats = GenerationStats.compute(3, [])
        self.assertEqual(stats.population, 0)
        self.assertEqual(stats.best, -math.inf)
        self.assertEqual(stats.diversity, 0.0)

    def test_identical_strategies_have_zero_diversity(self):
        agents = [make_agent(1.0, focus=0.5, iteration=10, risk=0.5) for _ in range(10)]
        stats = GenerationStats.compute(0, agents)
        self.assertEqual(stats.diversity, 0.0)

    def test_maximally_different_strategies_have_diversity_one(self):
        agents = [make_agent(1.0, 0.0, 1, 0.0), make_agent(1.0, 1.0, 20, 1.0)]
        stats = GenerationStats.compute(0, agents)
        self.assertAlmostEqual(stats.diversity, 1.0)

    def test_mean_strategy_tracked(self):
        agents = [make_agent(1.0, 0.0, 10, 1.0), make_agent(1.0, 1.0, 20, 0.0)]
        stats = GenerationStats.compute(0, agents)
        self.assertAlmostEqual(stats.mean_strategy["focus"], 0.5)
        self.assertAlmostEqual(stats.mean_strategy["iteration"], 15.0)
        self.assertAlmostEqual(stats.mean_strategy["risk_taking"], 0.5)

    def test_as_dict_is_json_serializable(self):
        import json

        agents = [make_agent(1.0)]
        json.dumps(GenerationStats.compute(0, agents).as_dict())

    def test_negative_infinity_scores_are_ignored(self):
        agents = [make_agent(1.0)]
        agents.append(Agent())  # unacted, score = -inf
        stats = GenerationStats.compute(0, agents)
        self.assertEqual(stats.best, 1.0)
        self.assertEqual(stats.mean, 1.0)


class TestRunResult(unittest.TestCase):
    def _result(self, bests):
        stats = [
            GenerationStats(
                generation=i,
                population=10,
                best=b,
                mean=b - 1,
                median=b - 1,
                stdev=0.1,
                diversity=0.2,
                evaluations=100 * (i + 1),
            )
            for i, b in enumerate(bests)
        ]
        return RunResult(
            problem="sphere",
            seed=1,
            config={"GENERATIONS": len(bests)},
            stats=stats,
            best_agent=None,
            wall_time=0.5,
        )

    def test_summary_numbers(self):
        result = self._result([-5.0, -2.0, -1.0])
        s = result.summary()
        self.assertEqual(s["generations"], 3)
        self.assertEqual(s["initial_best"], -5.0)
        self.assertEqual(s["final_best"], -1.0)
        self.assertAlmostEqual(s["improvement"], 4.0)
        self.assertEqual(s["best_overall"], -1.0)

    def test_convergence_detected_when_flat(self):
        result = self._result([-5.0, -1.0, -1.0, -1.0, -1.0, -1.0, -1.0])
        self.assertEqual(result.convergence_generation(), 1)

    def test_convergence_none_when_still_improving(self):
        result = self._result([-5.0, -4.0, -3.0, -2.0, -1.0, -0.5])
        self.assertIsNone(result.convergence_generation())

    def test_convergence_none_when_too_short(self):
        result = self._result([-5.0, -1.0])
        self.assertIsNone(result.convergence_generation())

    def test_empty_summary(self):
        result = self._result([])
        self.assertEqual(result.summary(), {})

    def test_series(self):
        result = self._result([-3.0, -2.0, -1.0])
        self.assertEqual(result.series("best"), [-3.0, -2.0, -1.0])


class TestConfig(unittest.TestCase):
    def test_defaults(self):
        config = load_config()
        self.assertEqual(config.INITIAL_AGENTS, 5)
        self.assertEqual(config.MAX_AGENTS, 50)
        self.assertEqual(config.GENERATIONS, 20)
        self.assertEqual(config.PROBLEM, "rastrigin")

    def test_env_overrides(self):
        config = load_config({"AGENTLEGION_MAX_AGENTS": "99"})
        self.assertEqual(config.MAX_AGENTS, 99)

    def test_env_override_beaten_by_explicit_kwarg(self):
        config = load_config({"AGENTLEGION_MAX_AGENTS": "99"}, MAX_AGENTS=7)
        self.assertEqual(config.MAX_AGENTS, 7)

    def test_invalid_env_value_raises(self):
        with self.assertRaises(ConfigError):
            load_config({"AGENTLEGION_MAX_AGENTS": "many"})

    def test_replace(self):
        config = load_config().replace(SEED=42)
        self.assertEqual(config.SEED, 42)

    def test_replace_unknown_key_raises(self):
        with self.assertRaises(ConfigError):
            load_config().replace(NOPE=1)

    def test_unknown_kwarg_raises(self):
        with self.assertRaises(ConfigError):
            load_config(BOGUS=1)

    def test_use_mock_llm_logic(self):
        self.assertTrue(load_config(LLM_BACKEND="mock").USE_MOCK_LLM)
        self.assertTrue(load_config(LLM_BACKEND="auto", OPENAI_API_KEY="").USE_MOCK_LLM)
        self.assertFalse(load_config(LLM_BACKEND="auto", OPENAI_API_KEY="sk-x").USE_MOCK_LLM)
        self.assertFalse(load_config(LLM_BACKEND="openai", OPENAI_API_KEY="sk-x").USE_MOCK_LLM)

    def test_as_dict_masks_api_key(self):
        config = load_config(OPENAI_API_KEY="sk-super-secret")
        self.assertEqual(config.as_dict()["OPENAI_API_KEY"], "***")

    def test_empty_env_value_falls_back_to_default(self):
        config = load_config({"AGENTLEGION_MAX_AGENTS": ""})
        self.assertEqual(config.MAX_AGENTS, 50)

    def test_seed_zero_is_preserved(self):
        self.assertEqual(load_config(SEED=0).SEED, 0)


if __name__ == "__main__":
    unittest.main()
