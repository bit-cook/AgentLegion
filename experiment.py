from agent_legion.environment import Environment
from config import Config
import csv

def run_experiment(trials=5):
    results = []
    print(f"Running {trials} experimental trials...")
    
    for i in range(trials):
        print(f"Trial {i+1}...")
        env = Environment(Config)
        
        trial_data = {
            "trial": i+1,
            "generations": []
        }
        
        for gen in range(Config.GENERATIONS):
            env.run_generation()
            trial_data["generations"].append({
                "generation": gen,
                "best_score": env.best_agent.score,
                "population": len(env.agents)
            })
            
        results.append(trial_data)

    # Save to CSV
    with open("experiment_results.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Trial", "Generation", "Best_Score", "Population"])
        
        for trial in results:
            for gen_data in trial["generations"]:
                writer.writerow([
                    trial["trial"],
                    gen_data["generation"],
                    f"{gen_data['best_score']:.2f}",
                    gen_data["population"]
                ])
                
    print("\nExperiment complete. Results saved to 'experiment_results.csv'.")

if __name__ == "__main__":
    run_experiment()
