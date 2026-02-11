import os

class Config:
    MAX_AGENTS = 50
    INITIAL_AGENTS = 5
    GENERATIONS = 10
    MUTATION_RATE = 0.1
    SURVIVAL_RATE = 0.5
    PROBLEM_COMPLEXITY = 100
    
    # LLM Configuration (Mock if API key not present)
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
    USE_MOCK_LLM = True # Force mock for now due to install issues
