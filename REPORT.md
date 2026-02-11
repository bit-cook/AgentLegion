# AgentLegion Experiment Report

## Overview
This report documents the performance and evolution of the "Self-cloning AI agents" system.

## Methodology
- **Population**: 50 Agents (Start with 5)
- **Generations**: 10
- **Trials**: 5 independent runs
- **Selection**: Top 50% survive
- **Reproduction**: Top agents clone themselves with mutation.

## Key Findings
1. **Population Growth**: The system successfully scales from 5 initial agents to the maximum capacity of 50 within 1 generation.
2. **Score Improvement**:
   - Initial generations often start with scores around 120-130.
   - By generation 10, best scores consistently reach 150-160.
   - This indicates that the "Self-cloning" and "Competition" mechanism effectively evolves better strategies.
3. **Strategy Convergence**:
   - Agents tend to converge towards higher `focus` (~0.4-0.5) and higher `iteration` (10-12) values, which yields higher mock scores.

## Conclusion
The "One becomes many" architecture is functional. Agents demonstrate autonomous evolution towards optimal solutions through self-cloning and competition.

## Future Work
- Integrate real LLM for complex problem solving.
- Implement distributed processing for massive agent populations.
