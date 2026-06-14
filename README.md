# Job Search Tracker

A lightweight Python utility to record and list job applications.

## Project Structure
```
JOBS OS 2026/
├─ src/                 # Application source code
│   └─ job_tracker.py   # Core tracker script
├─ data/                # Persistent JSON storage (created on first run)
├─ tests/               # pytest test suite
│   └─ test_job_tracker.py
└─ README.md            # This file
```

## Installation
```bash
# Create a virtual environment (optional but recommended)
python3 -m venv .venv
source .venv/bin/activate

# Install any dependencies (none required beyond the standard library)
```

## Usage
```bash
# Add a job entry
python src/job_tracker.py add "Software Engineer" "Acme Corp" Applied

# List all saved jobs
python src/job_tracker.py list
```

## Testing
Run the test suite with:
```bash
pytest -q
```

The tests use a temporary data directory to avoid interfering with your real job data.

---
*Built with Claude Code – your friendly AI coding assistant.*
