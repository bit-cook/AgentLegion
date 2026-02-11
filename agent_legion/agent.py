import uuid
import random
import copy
from .llm import LLMProvider

class Agent:
    def __init__(self, generation=0, parent_id=None, strategy=None):
        self.id = str(uuid.uuid4())[:8]
        self.parent_id = parent_id
        self.generation = generation
        self.strategy = strategy if strategy else self._random_strategy()
        self.score = 0
        self.llm = LLMProvider()
        self.is_alive = True

    def _random_strategy(self):
        return {
            "focus": random.random(),     # 0.0 to 1.0
            "iteration": random.randint(1, 10),
            "risk_taking": random.random()
        }

    def act(self, problem):
        """
        Attempt to solve the problem using current strategy.
        """
        solution = self.llm.generate_solution(problem, self.strategy)
        self.score = self.llm.evaluate_solution(solution)
        return self.score

    def clone(self):
        """
        Self-cloning with mutation.
        """
        new_strategy = copy.deepcopy(self.strategy)
        
        # Mutation logic
        if random.random() < 0.5:
            new_strategy["focus"] = min(1.0, max(0.0, new_strategy["focus"] + random.uniform(-0.1, 0.1)))
        
        if random.random() < 0.5:
            new_strategy["iteration"] = max(1, new_strategy["iteration"] + random.randint(-1, 1))
            
        child = Agent(
            generation=self.generation + 1,
            parent_id=self.id,
            strategy=new_strategy
        )
        return child

    def __repr__(self):
        return f"<Agent {self.id} Gen{self.generation} Score={self.score:.2f}>"
