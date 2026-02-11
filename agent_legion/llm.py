import random

class LLMProvider:
    def __init__(self, use_mock=True):
        self.use_mock = use_mock

    def generate_solution(self, problem_description, strategy):
        """
        Generates a solution score (simulated) based on strategy quality.
        In a real scenario, this would return a code snippet or text solution.
        """
        if self.use_mock:
            # Simulate solution quality based on strategy "fitness" (hidden)
            # Strategy is assumed to be a dictionary of parameters
            base_score = random.uniform(0, 100)
            
            # If strategy has 'aggression' or 'precision', use them
            bonus = 0
            if isinstance(strategy, dict):
                bonus += strategy.get('focus', 0) * 10
                bonus += strategy.get('iteration', 0) * 5
            
            return f"Solution Score: {base_score + bonus:.2f}"
        else:
            # Call OpenAI API (Not implemented due to dependency issues)
            return "Real LLM not available"

    def evaluate_solution(self, solution):
        """
        Parses the solution string to extract a score.
        """
        try:
            if "Solution Score:" in solution:
                return float(solution.split(":")[1].strip())
            return 0.0
        except:
            return 0.0
