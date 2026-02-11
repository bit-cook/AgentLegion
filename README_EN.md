# AgentLegion

**Self-cloning AI agents that compete for optimal solutions. One becomes many.**

## Overview
AgentLegion is a framework for autonomous AI agents capable of recursive self-replication (cloning) to explore vast solution spaces. Agents compete for resources and survival, driving the evolution of optimal strategies.

## Core Concepts
- **Self-Cloning**: Agents can spawn child agents to delegate subtasks or explore alternative paths.
- **Competition**: Agents are evaluated based on performance. Low-performing agents are pruned.
- **Evolution**: Successful traits and strategies are propagated to new generations.

## Installation
1. Clone the repository.
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Configure `.env` file with your API keys.

## Usage
Run the demo:
```bash
python main.py
```

## Running Experiments
To run the evolution experiment and generate a report:
```bash
python experiment.py
```
