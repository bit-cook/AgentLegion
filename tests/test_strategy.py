import random
import unittest

from agent_legion.strategy import GENE_SPECS, Strategy


class TestStrategy(unittest.TestCase):
    def test_random_within_bounds(self):
        rng = random.Random(0)
        for _ in range(200):
            s = Strategy.random(rng)
            self.assertTrue(0.0 <= s.focus <= 1.0)
            self.assertTrue(1 <= s.iteration <= 20)
            self.assertTrue(0.0 <= s.risk_taking <= 1.0)

    def test_construction_clamps_out_of_range_values(self):
        s = Strategy(focus=5.0, iteration=99, risk_taking=-3.0)
        self.assertEqual(s.focus, 1.0)
        self.assertEqual(s.iteration, 20)
        self.assertEqual(s.risk_taking, 0.0)

    def test_construction_rejects_nan(self):
        s = Strategy(focus=float("nan"), iteration=1, risk_taking=0.5)
        self.assertEqual(s.focus, 0.0)

    def test_from_mapping(self):
        s = Strategy.from_mapping({"focus": 0.2, "iteration": 7, "risk_taking": 0.9})
        self.assertEqual((s.focus, s.iteration, s.risk_taking), (0.2, 7, 0.9))

    def test_from_mapping_missing_gene_raises(self):
        with self.assertRaises(KeyError):
            Strategy.from_mapping({"focus": 0.2, "iteration": 7})

    def test_mutation_rate_zero_is_identity(self):
        s = Strategy(0.3, 10, 0.6)
        self.assertEqual(s.mutated(random.Random(1), rate=0.0), s)

    def test_mutation_is_deterministic_for_seed(self):
        s = Strategy(0.3, 10, 0.6)
        a = s.mutated(random.Random(42), rate=0.5)
        b = s.mutated(random.Random(42), rate=0.5)
        self.assertEqual(a, b)

    def test_mutation_rate_one_changes_at_least_one_gene(self):
        s = Strategy(0.3, 10, 0.6)
        child = s.mutated(random.Random(7), rate=1.0)
        self.assertNotEqual(child, s)

    def test_mutated_child_stays_in_bounds(self):
        rng = random.Random(3)
        s = Strategy(0.99, 19, 0.99)
        for _ in range(200):
            child = s.mutated(rng, rate=1.0)
            for name, (lo, hi, _kind) in GENE_SPECS.items():
                value = getattr(child, name)
                self.assertGreaterEqual(value, lo)
                self.assertLessEqual(value, hi)

    def test_invalid_mutation_rate_raises(self):
        s = Strategy(0.3, 10, 0.6)
        with self.assertRaises(ValueError):
            s.mutated(random.Random(1), rate=1.5)

    def test_crossover_takes_each_gene_from_a_parent(self):
        a = Strategy(0.1, 2, 0.1)
        b = Strategy(0.9, 18, 0.9)
        rng = random.Random(11)
        for _ in range(50):
            child = a.crossover(b, rng)
            self.assertIn(child.focus, (0.1, 0.9))
            self.assertIn(child.iteration, (2, 18))
            self.assertIn(child.risk_taking, (0.1, 0.9))

    def test_distance(self):
        a = Strategy(0.5, 10, 0.5)
        self.assertEqual(a.distance(a), 0.0)
        lo = Strategy(0.0, 1, 0.0)
        hi = Strategy(1.0, 20, 1.0)
        self.assertAlmostEqual(lo.distance(hi), 1.0)

    def test_distance_is_symmetric(self):
        a = Strategy(0.1, 3, 0.8)
        b = Strategy(0.7, 15, 0.2)
        self.assertAlmostEqual(a.distance(b), b.distance(a))

    def test_as_dict_roundtrip(self):
        s = Strategy(0.42, 7, 0.13)
        self.assertEqual(Strategy.from_mapping(s.as_dict()), s)


if __name__ == "__main__":
    unittest.main()
