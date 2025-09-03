# pydomjudge

A Python wrapper for the DOMJudge API. Easily interact with DOMJudge contest management systems from your Python code.

## Features
- Full API coverage for DOMJudge v4 endpoints
- Pydantic models for all major entities (Contest, Team, Submission, etc.)
- Simple, unified client interface (`DOMJudge`)
- Supports authentication, file uploads, and more
- Designed for scripting, automation, and integration

## Planned / To Do

- Add more automatic tests and CI integration
- Expand documentation and usage examples
- Add more API endpoint coverage as DOMJudge evolves
- Improve error handling and type hints

## Installation

```bash
pip install pydomjudge
```
Or clone this repository and install locally:
```bash
git clone https://github.com/xivqn/pydomjudge.git
cd pydomjudge
pip install .
```

## Requirements
- Python 3.8+
- [DOMJudge](https://www.domjudge.org/) instance (for API access)
- See `requirements.txt` for dependencies

## Usage Example

```python
from pydomjudge import DOMJudge

dj = DOMJudge("http://localhost/domjudge", "admin", "adminpass")
contests = dj.get_all_contests()
for contest in contests:
    print(contest.name, contest.start_time)
```

## Project Structure

```
pydomjudge/
├── src/pydomjudge/
│   ├── domjudge.py         # Main unified client
│   ├── clients/           # API endpoint clients (teams, users, problems, etc.)
│   └── models/            # Pydantic models for API objects
├── tests/                 # Unit and integration tests
├── requirements.txt       # Runtime dependencies
├── requirements-test.txt  # Test/development dependencies
├── pyproject.toml         # Build system and metadata
├── README.md              # This file
```

## Testing

Install test dependencies:
```bash
pip install -r requirements-test.txt
```
Run tests:
```bash
pytest
```

## License

This project is licensed under the GNU GPL v3. See [LICENSE](LICENSE) for details.

## Links
- [DOMJudge](https://www.domjudge.org/)
- [GitHub Repository](https://github.com/xivqn/pydomjudge)
