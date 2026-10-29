import math
import random
import unittest

from agent_legion.agent import Agent
from agent_legion.llm import MockLLM
from agent_legion.problems import get_problem
from agent_legion.strategy import Strategy


def make_agent(**kwargs):
    kwargs.setdefault("llm", MockLLM())
    kwargs.setdefault("rng", random.Random(kwargs.pop("seed", 0)))
    return Agent(**kwargs)


class TestAgent(unittest.TestCase):
    def test_initialization_defaults(self):
        agent = make_agent()
        self.assertEqual(len(agent.id), 8)
        self.assertEqual(agent.generation, 0)
        self.assertIsNone(agent.parent_id)
        self.assertEqual(agent.parent_ids, ())
        self.assertIsInstance(agent.strategy, Strategy)
        self.assertTrue(agent.is_alive)
        self.assertIsNone(agent.incumbent_x)
        self.assertEqual(agent.score, -math.inf)

    def test_act_updates_incumbent_and_score(self):
        rng = random.Random(1)
        agent = make_agent(rng=rng)
        problem = get_problem("sphere")
        score = agent.act(problem)
        self.assertTrue(math.isfinite(score))
        self.assertEqual(agent.score, score)
        self.assertIsNotNone(agent.incumbent_x)
        self.assertLessEqual(agent.score, 0.0)  # sphere optimum is 0.0
        self.assertGreater(agent.evaluations, 0)

    def test_score_is_monotone_non_decreasing(self):
        rng = random.Random(2)
        agent = make_agent(rng=rng)
        problem = get_problem("rastrigin")
        previous = -math.inf
        for _ in range(10):
            score = agent.act(problem)
            self.assertGreaterEqual(score, previous)
            previous = score

    def test_iteration_controls_sample_count(self):
        rng = random.Random(3)
        agent = make_agent(rng=rng, strategy=Strategy(0.5, 5, 0.5))
        problem = get_problem("sphere")
        agent.act(problem)
        self.assertEqual(agent.evaluations, 5)

    def test_clone_lineage_and_inheritance(self):
        rng = random.Random(4)
        parent = make_agent(rng=rng, strategy=Strategy(0.5, 10, 0.5))
        parent.act(get_problem("sphere"))
        child = parent.clone(mutation_rate=0.0)
        self.assertEqual(child.parent_id, parent.id)
        self.assertEqual(child.generation, parent.generation + 1)
        self.assertNotEqual(child.id, parent.id)
        self.assertEqual(child.strategy, parent.strategy)  # rate 0 -> identical
        self.assertEqual(child.incumbent_x, parent.incumbent_x)
        self.assertIs(child.llm, parent.llm)

    def test_breed_records_both_parents(self):
        rng = random.Random(5)
        a = make_agent(rng=rng)
        b = make_agent(rng=rng)
        child = a.breed(b, mutation_rate=0.0)
        self.assertEqual(child.parent_ids, (a.id, b.id))
        self.assertEqual(child.generation, 1)

    def test_breed_rejects_non_agent(self):
        with self.assertRaises(TypeError):
            make_agent().breed("not an agent")  # type: ignore[arg-type]

    def test_breed_inherits_better_parent_incumbent(self):
        rng = random.Random(6)
        problem = get_problem("sphere")
        weak = make_agent(rng=rng)
        strong = make_agent(rng=rng)
        weak.act(problem)
        strong.act(problem)
        better, worse = (weak, strong) if weak.score >= strong.score else (strong, weak)
        child = better.breed(worse)
        self.assertEqual(child.incumbent_x, better.incumbent_x)

    def test_describe_serializable(self):
        agent = make_agent()
        agent.act(get_problem("sphere"))
        data = agent.describe()
        self.assertEqual(data["id"], agent.id)
        self.assertAlmostEqual(data["score"], agent.score)
        self.assertIn("strategy", data)

    def test_repr_before_and_after_acting(self):
        agent = make_agent()
        self.assertIn("n/a", repr(agent))
        agent.act(get_problem("sphere"))
        self.assertIn("Score=", repr(agent))


if __name__ == "__main__":
    unittest.main()
