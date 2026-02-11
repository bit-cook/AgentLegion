import unittest
from agent_legion.environment import Environment
from config import Config

class TestEnvironment(unittest.TestCase):
    def setUp(self):
        self.config = Config
        self.config.INITIAL_AGENTS = 5
        self.config.MAX_AGENTS = 10
        self.config.SURVIVAL_RATE = 0.5
        self.env = Environment(self.config)

    def test_initial_population(self):
        self.assertEqual(len(self.env.agents), 5)

    def test_run_generation(self):
        self.env.run_generation()
        # Population should grow or stay same, max 10
        self.assertLessEqual(len(self.env.agents), 10)
        self.assertGreater(len(self.env.agents), 0)
        
        # Best agent should be identified
        self.assertIsNotNone(self.env.best_agent)

if __name__ == '__main__':
    unittest.main()
