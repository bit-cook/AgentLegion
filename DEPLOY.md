# Deployment Guide

## Prerequisites
- Python 3.7+
- Pip (Python Package Installer)

## Setup Steps
1. **Clone the Repository**
   ```bash
   git clone <repository_url>
   cd AgentLegion
   ```

2. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```
   *Note: If `openai` installation fails due to network issues, the system will automatically fall back to the built-in `MockLLM` provider.*

3. **Configuration**
   - No additional configuration is needed for the Mock mode.
   - To use real LLM, set `OPENAI_API_KEY` in `config.py` or as an environment variable, and change `USE_MOCK_LLM = False`.

## Running the Application
- **Basic Demo**:
  ```bash
  python main.py
  ```
- **Run Experiments**:
  ```bash
  python experiment.py
  ```
- **Run Tests**:
  ```bash
  python -m unittest discover tests
  ```

## Troubleshooting
- **SSL Errors**: Ensure you are using a Python version that supports modern SSL (Python 3.7+ recommended).
- **Import Errors**: Ensure you run commands from the project root directory.
