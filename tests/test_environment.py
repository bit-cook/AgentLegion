import math
import random
import unittest

from agent_legion.agent import Agent
from agent_legion.config import ConfigError, load_config
from agent_legion.environment import Environment
from agent_legion.llm import MockLLM
from agent_legion.metrics import GenerationStats
from agent_legion.problems import get_problem
from agent_legion.strategy import Strategy


def small_config(**overrides):
    base = dict(
        INITIAL_AGENTS=6,
        MAX_AGENTS=12,
        GENERATIONS=8,
        SEED=123,
        LLM_BACKEND="mock",
        PROBLEM="sphere",
    )
    base.update(overrides)
    return load_config({}).replace(**base)


class TestEnvironment(unittest.TestCase):
    def test_initial_population_size(self):
        env = Environment(small_config())
        self.assertEqual(len(env.agents), 6)
        self.assertEqual(env.generation, 0)
        self.assertIsNone(env.best_agent)
        self.assertEqual(env.history, [])

    def test_accepts_config_class_for_backwards_compat(self):
        from config import Config  # historical shim

        env = Environment(Config, seed=5)
        self.assertGreater(len(env.agents), 0)

    def test_run_generation_invariants(self):
        env = Environment(small_config())
        stats = env.run_generation()
        self.assertIsInstance(stats, GenerationStats)
        self.assertLessEqual(len(env.agents), 12)
        self.assertGreaterEqual(len(env.agents), 1)
        self.assertIsNotNone(env.best_agent)
        assert env.best_agent is not None
        self.assertEqual(len(env.history), 1)
        self.assertEqual(env.generation, 1)
        self.assertAlmostEqual(stats.best, env.best_agent.score)

    def test_best_score_is_monotone_non_decreasing(self):
        env = Environment(small_config(PROBLEM="rastrigin", GENERATIONS=15))
        previous = -math.inf
        for _ in range(15):
            stats = env.run_generation()
            self.assertGreaterEqual(stats.best, previous - 1e-12)
            previous = stats.best

    def test_population_grows_to_cap_then_stays(self):
        env = Environment(small_config())
        env.run_generation()
        self.assertEqual(len(env.agents), 12)
        env.run_generation()
        self.assertEqual(len(env.agents), 12)

    def test_seeded_runs_are_reproducible(self):
        def series():
            env = Environment(small_config(PROBLEM="rastrigin", GENERATIONS=10))
            env.run_simulation()
            return [s.best for s in env.history]

        self.assertEqual(series(), series())

    def test_different_seeds_diverge(self):
        a = Environment(small_config(SEED=1, GENERATIONS=10)).run_simulation()
        b = Environment(small_config(SEED=2, GENERATIONS=10)).run_simulation()
        self.assertNotEqual(a.series("best"), b.series("best"))

    def test_evolution_actually_improves_on_sphere(self):
        env = Environment(small_config(PROBLEM="sphere", GENERATIONS=25, MAX_AGENTS=16))
        result = env.run_simulation()
        first, last = result.stats[0].best, result.stats[-1].best
        self.assertGreater(last, first)
        self.assertGreater(last, -1.0)  # gets close to the 0.0 optimum

    def test_previous_best_score_never_decreases(self):
        env = Environment(small_config(PROBLEM="rastrigin"))
        env.run_generation()
        previous_best = env.best_score
        env.run_generation()
        # every agent's incumbent score is monotone, and the previous top
        # scorer keeps acting, so the population maximum cannot fall
        self.assertGreaterEqual(env.best_score, previous_best)

    def test_exactly_elite_count_agents_survive_untouched(self):
        env = Environment(small_config(ELITE_RATE=0.25))
        env.run_generation()
        previous = {a.id: a.strategy for a in env.agents}
        elite_count = max(1, int(len(env.agents) * 0.25))
        env.run_generation()
        carried_over = [a for a in env.agents if a.id in previous]
        # elites keep their identity and their exact strategy; every other
        # slot is a freshly created child with a new id
        self.assertEqual(len(carried_over), elite_count)
        for agent in carried_over:
            self.assertEqual(agent.strategy, previous[agent.id])

    def test_surviving_agents_never_lose_score(self):
        env = Environment(small_config())
        env.run_generation()
        before = {a.id: a.score for a in env.agents}
        env.run_generation()
        for agent in env.agents:
            if agent.id in before:
                self.assertGreaterEqual(agent.score, before[agent.id])

    def test_injected_llm_is_shared_by_all_agents(self):
        llm = MockLLM()
        env = Environment(small_config(), llm=llm)
        self.assertTrue(all(a.llm is llm for a in env.agents))

    def test_injected_problem_is_used(self):
        problem = get_problem("rosenbrock")
        env = Environment(small_config(), problem=problem)
        env.run_generation()
        self.assertEqual(env.problem.name, "rosenbrock")

    def test_config_validation_rejects_bad_population(self):
        with self.assertRaises(ConfigError):
            Environment(small_config(INITIAL_AGENTS=20, MAX_AGENTS=10))

    def test_config_validation_rejects_bad_mutation_rate(self):
        with self.assertRaises(ConfigError):
            Environment(small_config(MUTATION_RATE=1.5))

    def test_config_validation_rejects_missing_key(self):
        class Broken:
            INITIAL_AGENTS = 5
            MAX_AGENTS = 10
            GENERATIONS = 3
            MUTATION_RATE = 0.1
            ELITE_RATE = 0.1
            CROSSOVER_RATE = 0.5
            # TOURNAMENT_SIZE missing

        with self.assertRaises(ConfigError):
            Environment(Broken())

    def test_run_simulation_returns_result(self):
        env = Environment(small_config(GENERATIONS=6))
        result = env.run_simulation()
        self.assertEqual(len(result.stats), 6)
        self.assertEqual(result.problem, "sphere")
        self.assertIsNotNone(result.best_agent)
        self.assertGreater(result.wall_time, 0.0)

    def test_generations_argument_overrides_config(self):
        env = Environment(small_config(GENERATIONS=3))
        result = env.run_simulation(generations=5)
        self.assertEqual(len(result.stats), 5)

    def test_elites_are_never_mutated(self):
        env = Environment(small_config(ELITE_RATE=0.5))
        env.run_generation()
        elites = env.agents[:6]
        env.run_generation()
        surviving = [a for a in env.agents if a.id in {e.id for e in elites}]
        for agent in surviving:
            original = next(e for e in elites if e.id == agent.id)
            self.assertEqual(agent.strategy, original.strategy)

    def test_repr(self):
        env = Environment(small_config())
        env.run_generation()
        self.assertIn("Environment", repr(env))
        self.assertIn("sphere", repr(env))


if __name__ == "__main__":
    unittest.main()
