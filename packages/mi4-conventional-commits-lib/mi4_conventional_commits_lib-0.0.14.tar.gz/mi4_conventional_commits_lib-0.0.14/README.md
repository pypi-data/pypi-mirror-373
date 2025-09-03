# mi4-conventional-commits-lib

A Python library for validating conventional commits.

## Installation

```bash
pip install .
```

## Usage

```python
from mi4_conventional_commits_lib import parseCommit, isCommitValid, buildCommit, getCommitTypes

# Validate a commit
result = validateCommit("feat: new feature (#123)")
print(result)  # True

# Parse a commit
parsed = parseCommit("fix(auth)!: fix bug (#456)")
print(parsed)  # {'type': 'fix', 'scope': 'auth', ...}

# Build a commit
commit_obj = {
    "type": "feat",
    "scope": "api",
    "breakChange": True,
    "description": "new API",
    "issue": 789
}
built = buildCommit(commit_obj)
print(built)  # "feat(api)!: new API (#789)"
```

## Available Functions

- `parseCommit`: parseCommit function
- `isCommitValid`: isCommitValid function
- `buildCommit`: buildCommit function
- `getCommitTypes`: getCommitTypes function

## License

MIT License
