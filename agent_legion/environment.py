from .agent import Agent
import time

class Environment:
    def __init__(self, config):
        self.config = config
        self.agents = [Agent() for _ in range(config.INITIAL_AGENTS)]
        self.generation = 0
        self.best_agent = None

    def run_generation(self):
        print(f"\n--- Generation {self.generation} ---")
        print(f"Population: {len(self.agents)}")
        
        # 1. Action Phase
        for agent in self.agents:
            score = agent.act("Find optimal strategy")
            # print(f"Agent {agent.id} scored {score}")

        # 2. Evaluation Phase
        self.agents.sort(key=lambda x: x.score, reverse=True)
        self.best_agent = self.agents[0]
        print(f"Best Agent: {self.best_agent.id} (Score: {self.best_agent.score:.2f})")
        print(f"Strategy: {self.best_agent.strategy}")

        # 3. Selection (Pruning)
        survivor_count = max(1, int(len(self.agents) * self.config.SURVIVAL_RATE))
        survivors = self.agents[:survivor_count]
        print(f"Survivors: {len(survivors)}")

        # 4. Reproduction (Cloning)
        new_population = []
        new_population.extend(survivors)
        
        slots_available = self.config.MAX_AGENTS - len(survivors)
        
        # Top agents get to clone more
        if slots_available > 0 and len(survivors) > 0:
            for i in range(slots_available):
                parent = survivors[i % len(survivors)]
                child = parent.clone()
                new_population.append(child)

        self.agents = new_population
        self.generation += 1

    def run_simulation(self):
        start_time = time.time()
        for _ in range(self.config.GENERATIONS):
            self.run_generation()
            # time.sleep(0.5)
        
        end_time = time.time()
        print("\n=== Simulation Complete ===")
        print(f"Final Best Agent: {self.best_agent}")
        print(f"Total Time: {end_time - start_time:.4f}s")
