import math
import random
import unittest

from agent_legion.problems import (
    PROBLEMS,
    Problem,
    RastriginProblem,
    RosenbrockProblem,
    SphereProblem,
    get_problem,
)


class TestProblemOptima(unittest.TestCase):
    def test_sphere_optimum_at_origin(self):
        p = SphereProblem()
        self.assertEqual(p.name, "sphere")
        self.assertAlmostEqual(p.evaluate([0.0, 0.0]), 0.0)
        self.assertAlmostEqual(p.evaluate([1.0, 1.0]), -2.0)
        self.assertLess(p.evaluate([1.0, 1.0]), p.evaluate([0.5, 0.5]))

    def test_rastrigin_optimum_at_origin(self):
        p = RastriginProblem()
        self.assertAlmostEqual(p.evaluate([0.0, 0.0]), 0.0)
        # local optima exist at integer points — this is the multimodal trap
        self.assertLess(p.evaluate([1.0, 1.0]), 0.0)
        self.assertGreater(p.evaluate([1.0, 1.0]), p.evaluate([1.9, 1.9]))

    def test_rosenbrock_optimum_at_ones(self):
        p = RosenbrockProblem()
        self.assertAlmostEqual(p.evaluate([1.0, 1.0]), 0.0)
        self.assertLess(p.evaluate([0.0, 0.0]), 0.0)

    def test_all_problems_are_maximization_with_zero_optimum(self):
        for factory in (SphereProblem, RastriginProblem, RosenbrockProblem):
            problem = factory(dimension=3)
            optimum = [1.0 if problem.name == "rosenbrock" else 0.0] * 3
            self.assertAlmostEqual(problem.evaluate(optimum), 0.0, places=9)

    def test_dimension_mismatch_raises(self):
        p = SphereProblem(dimension=3)
        with self.assertRaises(ValueError):
            p.evaluate([1.0, 2.0])

    def test_random_point_within_bounds(self):
        rng = random.Random(0)
        p = get_problem("sphere")
        lo, hi = p.bounds
        for _ in range(50):
            point = p.random_point(rng)
            self.assertEqual(len(point), p.dimension)
            self.assertTrue(all(lo <= v <= hi for v in point))

    def test_clip(self):
        p = get_problem("sphere")
        lo, hi = p.bounds
        self.assertEqual(p.clip([99.0, -99.0]), [hi, lo])

    def test_get_problem_case_insensitive(self):
        self.assertIsInstance(get_problem("RASTRIGIN"), RastriginProblem)

    def test_get_problem_unknown_lists_available(self):
        with self.assertRaises(ValueError) as ctx:
            get_problem("banana")
        message = str(ctx.exception)
        for name in PROBLEMS:
            self.assertIn(name, message)

    def test_registry_entries_are_problems(self):
        for name in PROBLEMS:
            self.assertIsInstance(get_problem(name), Problem)

    def test_scores_are_finite_floats(self):
        rng = random.Random(1)
        for name in PROBLEMS:
            problem = get_problem(name)
            for _ in range(20):
                value = problem.evaluate(problem.random_point(rng))
                self.assertIsInstance(value, float)
                self.assertTrue(math.isfinite(value))
                self.assertLessEqual(value, 0.0)


if __name__ == "__main__":
    unittest.main()
