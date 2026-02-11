import unittest
from agent_legion.agent import Agent

class TestAgent(unittest.TestCase):
    def test_initialization(self):
        agent = Agent()
        self.assertIsNotNone(agent.id)
        self.assertEqual(agent.generation, 0)
        self.assertIsNotNone(agent.strategy)

    def test_act(self):
        agent = Agent()
        score = agent.act("test problem")
        self.assertGreaterEqual(score, 0)
        self.assertEqual(agent.score, score)

    def test_clone(self):
        parent = Agent()
        child = parent.clone()
        
        self.assertEqual(child.parent_id, parent.id)
        self.assertEqual(child.generation, parent.generation + 1)
        self.assertNotEqual(child.id, parent.id)
        # Strategy might be mutated, but should exist
        self.assertIsNotNone(child.strategy)

if __name__ == '__main__':
    unittest.main()
