from agent_legion.environment import Environment
from config import Config
import sys

def main():
    print("Initializing AgentLegion...")
    print(f"Configuration: Max Agents={Config.MAX_AGENTS}, Generations={Config.GENERATIONS}")
    
    env = Environment(Config)
    env.run_simulation()

if __name__ == "__main__":
    main()
