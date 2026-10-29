import json
import random
import unittest
import urllib.error

from agent_legion.llm import (
    ConfigError,
    LLMError,
    MockLLM,
    OpenAILLM,
    Solution,
    create_llm,
)
from agent_legion.problems import get_problem
from agent_legion.strategy import Strategy


def cfg(**kwargs):
    from agent_legion.config import load_config

    return load_config(**kwargs)


class TestMockLLM(unittest.TestCase):
    def test_deterministic_for_seed(self):
        problem = get_problem("sphere")
        strategy = Strategy(0.5, 5, 0.5)
        a = MockLLM().propose(problem, strategy, None, random.Random(99))
        b = MockLLM().propose(problem, strategy, None, random.Random(99))
        self.assertEqual(a, b)

    def test_respects_iteration_count(self):
        problem = get_problem("sphere")
        solution = MockLLM().propose(problem, Strategy(0.5, 7, 0.5), None, random.Random(1))
        self.assertEqual(solution.samples, 7)
        self.assertEqual(solution.source, "mock")

    def test_score_matches_problem_evaluation(self):
        problem = get_problem("rastrigin")
        solution = MockLLM().propose(problem, Strategy(0.3, 4, 0.7), None, random.Random(2))
        self.assertAlmostEqual(solution.score, problem.evaluate(solution.x))

    def test_proposals_stay_in_bounds(self):
        problem = get_problem("sphere")
        lo, hi = problem.bounds
        for seed in range(20):
            solution = MockLLM().propose(
                problem, Strategy(0.0, 20, 1.0), None, random.Random(seed)
            )
            for v in solution.x:
                self.assertGreaterEqual(v, lo)
                self.assertLessEqual(v, hi)

    def test_high_focus_keeps_samples_near_incumbent(self):
        problem = get_problem("sphere")
        lo, hi = problem.bounds
        span = hi - lo
        incumbent = [1.0, -1.0]
        solution = MockLLM().propose(
            problem, Strategy(1.0, 30, 0.0), incumbent, random.Random(5)
        )
        deviation = max(abs(a - b) for a, b in zip(solution.x, incumbent))
        self.assertLess(deviation, span * 0.05)

    def test_high_risk_explores_widely(self):
        problem = get_problem("sphere")
        lo, hi = problem.bounds
        span = hi - lo
        incumbent = [0.0, 0.0]
        solution = MockLLM().propose(
            problem, Strategy(0.0, 30, 1.0), incumbent, random.Random(5)
        )
        deviation = max(abs(a - b) for a, b in zip(solution.x, incumbent))
        self.assertGreater(deviation, span * 0.1)


class TestOpenAILLM(unittest.TestCase):
    def _strategy(self):
        return Strategy(0.5, 2, 0.5)

    def test_parse_plain_json(self):
        problem = get_problem("sphere")
        x = OpenAILLM._parse_solution('{"x": [0.1, 0.2]}', problem)
        self.assertEqual(x, [0.1, 0.2])

    def test_parse_json_with_markdown_fence(self):
        problem = get_problem("sphere")
        x = OpenAILLM._parse_solution('```json\n{"x": [1, 2]}\n```', problem)
        self.assertEqual(x, [1.0, 2.0])

    def test_parse_rejects_wrong_dimension(self):
        problem = get_problem("sphere")
        with self.assertRaises(LLMError):
            OpenAILLM._parse_solution('{"x": [1, 2, 3]}', problem)

    def test_parse_rejects_non_numeric(self):
        problem = get_problem("sphere")
        with self.assertRaises(LLMError):
            OpenAILLM._parse_solution('{"x": ["a", "b"]}', problem)

    def test_parse_rejects_garbage(self):
        problem = get_problem("sphere")
        with self.assertRaises(LLMError):
            OpenAILLM._parse_solution("I refuse to answer", problem)

    def test_parse_clips_out_of_bounds(self):
        problem = get_problem("sphere")
        lo, hi = problem.bounds
        x = OpenAILLM._parse_solution('{"x": [99, -99]}', problem)
        self.assertEqual(x, [hi, lo])

    def test_transport_injection(self):
        problem = get_problem("sphere")

        def fake_transport(url, payload, headers):
            self.assertIn("/chat/completions", url)
            self.assertEqual(headers["Authorization"], "Bearer test-key")
            self.assertEqual(payload["model"], "test-model")
            return {
                "choices": [{"message": {"content": '{"x": [0.5, 0.5]}'}}]
            }

        llm = OpenAILLM(api_key="test-key", model="test-model", transport=fake_transport)
        solution = llm.propose(problem, self._strategy(), None, random.Random(0))
        self.assertEqual(solution.x, (0.5, 0.5))
        self.assertAlmostEqual(solution.score, -0.5)
        self.assertEqual(solution.source, "openai")

    def test_caps_samples_at_max_samples(self):
        problem = get_problem("sphere")
        calls = []

        def fake_transport(url, payload, headers):
            calls.append(1)
            return {"choices": [{"message": {"content": '{"x": [0.5, 0.5]}'}}]}

        llm = OpenAILLM(api_key="k", transport=fake_transport, max_samples=2)
        llm.propose(problem, Strategy(0.5, 20, 0.5), None, random.Random(0))
        self.assertEqual(len(calls), 2)

    def test_transport_error_becomes_llm_error(self):
        problem = get_problem("sphere")

        def broken_transport(url, payload, headers):
            raise urllib.error.URLError("network down")

        llm = OpenAILLM(api_key="k", transport=broken_transport)
        with self.assertRaises(LLMError):
            llm.propose(problem, self._strategy(), None, random.Random(0))

    def test_malformed_response_becomes_llm_error(self):
        problem = get_problem("sphere")

        def bad_transport(url, payload, headers):
            return {"choices": [{"message": {"content": "not json at all"}}]}

        llm = OpenAILLM(api_key="k", transport=bad_transport)
        with self.assertRaises(LLMError):
            llm.propose(problem, self._strategy(), None, random.Random(0))

    def test_payload_mentions_problem_and_bounds(self):
        problem = get_problem("sphere")
        llm = OpenAILLM(api_key="k")
        payload = llm._build_payload(problem, self._strategy(), [1.0, 1.0])
        user_msg = payload["messages"][1]["content"]
        self.assertIn("sphere", user_msg)
        self.assertIn("[-5.12, 5.12]", user_msg)
        self.assertIn("[1.0, 1.0]", user_msg)


class TestCreateLLM(unittest.TestCase):
    def test_mock_backend_returns_mock(self):
        self.assertIsInstance(create_llm(cfg(LLM_BACKEND="mock")), MockLLM)

    def test_openai_backend_without_key_fails_loud(self):
        with self.assertRaises(ConfigError):
            create_llm(cfg(LLM_BACKEND="openai", OPENAI_API_KEY=""))

    def test_openai_backend_with_key_returns_openai(self):
        llm = create_llm(cfg(LLM_BACKEND="openai", OPENAI_API_KEY="sk-test"))
        self.assertIsInstance(llm, OpenAILLM)

    def test_auto_without_key_warns_and_returns_mock(self):
        with self.assertLogs("agent_legion.llm", level="WARNING") as captured:
            llm = create_llm(cfg(LLM_BACKEND="auto", OPENAI_API_KEY=""))
        self.assertIsInstance(llm, MockLLM)
        self.assertTrue(any("OPENAI_API_KEY" in line for line in captured.output))

    def test_auto_with_key_returns_openai(self):
        llm = create_llm(cfg(LLM_BACKEND="auto", OPENAI_API_KEY="sk-test"))
        self.assertIsInstance(llm, OpenAILLM)

    def test_unknown_backend_raises(self):
        with self.assertRaises(ConfigError):
            create_llm(cfg(LLM_BACKEND="telepathy"))


if __name__ == "__main__":
    unittest.main()
