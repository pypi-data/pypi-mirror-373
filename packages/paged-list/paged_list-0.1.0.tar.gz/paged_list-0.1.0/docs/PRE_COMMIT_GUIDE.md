# Pre-commit Configuration Example for Paged-List

## Installation

```bash
# Install pre-commit
pip install pre-commit

# Install the hooks
pre-commit install
```

## Configuration File: `.pre-commit-config.yaml`

```yaml
# Pre-commit configuration for paged-list
repos:
  # Code formatting with Black
  - repo: https://github.com/psf/black
    rev: 23.7.0
    hooks:
      - id: black
        language_version: python3.9
        args: [--line-length=88]

  # Import sorting with isort
  - repo: https://github.com/pycqa/isort
    rev: 5.12.0
    hooks:
      - id: isort
        args: [--profile=black]

  # Linting with flake8
  - repo: https://github.com/pycqa/flake8
    rev: 6.0.0
    hooks:
      - id: flake8
        args: [--max-line-length=88, --extend-ignore=E203,W503]

  # Type checking with mypy
  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.5.1
    hooks:
      - id: mypy
        additional_dependencies: [types-all]
        args: [--ignore-missing-imports]

  # Security scanning with bandit
  - repo: https://github.com/pycqa/bandit
    rev: 1.7.5
    hooks:
      - id: bandit
        args: [-r, paged_list/]

  # General file checks
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.4.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-added-large-files
        args: [--maxkb=1000]
      - id: check-merge-conflict
      - id: debug-statements

  # Run tests (optional - can be slow)
  - repo: local
    hooks:
      - id: pytest
        name: pytest
        entry: pytest
        language: python
        pass_filenames: false
        args: [tests/, -x]  # Stop on first failure
```

## What Each Hook Does

### **Code Quality:**

- **black**: Formats Python code consistently
- **isort**: Sorts and organizes imports
- **flake8**: Checks style and finds potential bugs
- **mypy**: Verifies type hints are correct

### **Security:**

- **bandit**: Scans for security vulnerabilities
- **check-merge-conflict**: Prevents committing merge conflicts

### **File Management:**

- **trailing-whitespace**: Removes extra whitespace
- **end-of-file-fixer**: Ensures files end with newline
- **check-added-large-files**: Prevents huge files (>1MB)
- **debug-statements**: Catches leftover print/pdb statements

### **Testing:**

- **pytest**: Runs your test suite (optional, can be slow)

## Example Workflow

### **Before Pre-commit:**

```bash
# Manual process (easy to forget)
$ black paged_list/
$ flake8 paged_list/
$ mypy paged_list/
$ pytest
$ git add .
$ git commit -m "Add feature"
```

### **With Pre-commit:**

```bash
# Automatic process
$ git add .
$ git commit -m "Add feature"

# Pre-commit runs all checks automatically:
black....................................................................Passed
isort....................................................................Passed
flake8...................................................................Passed
mypy.....................................................................Passed
bandit...................................................................Passed
trailing-whitespace...................................................... Passed
end-of-file-fixer........................................................ Passed

# If all pass, commit succeeds!
```

## Benefits for Paged-List

### **1. Maintain Code Quality**

Your project already has excellent test coverage (77%). Pre-commit would ensure:

- Consistent code formatting across all files
- No style violations
- Type safety maintained
- Security best practices

### **2. Prevent Common Issues**

- Catching bugs before they reach the repository
- Preventing accidentally committed debug statements
- Ensuring all files are properly formatted

### **3. Team Development**

When others contribute to paged-list:

- Automatic code formatting (no style discussions)
- Consistent quality standards
- Faster PR reviews (less back-and-forth on style)

## Configuration for Your Project

Based on your current setup, here's what I'd recommend:

```yaml
# Minimal but effective pre-commit config for paged-list
repos:
  - repo: https://github.com/psf/black
    rev: 23.7.0
    hooks:
      - id: black
        args: [--line-length=88]

  - repo: https://github.com/pycqa/flake8
    rev: 6.0.0
    hooks:
      - id: flake8
        args: [--max-line-length=88, --extend-ignore=E203]

  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.4.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-added-large-files
```

This gives you the most important checks without being overwhelming.

## Should You Add Pre-commit to Paged-List?

### **✅ Yes, because:**

- Your project is well-structured and would benefit from automation
- You already use black, flake8, mypy in tox.ini
- Would help maintain quality as project grows
- Easy to set up and low maintenance

### **⚠️ Consider:**

- Adds a small delay to commits (usually 2-10 seconds)
- Might occasionally block commits that need manual review
- Team members need to install pre-commit

## Getting Started

If you want to add pre-commit to paged-list:

1. **Add to pyproject.toml**:

```toml
[project.optional-dependencies]
dev = [
    "pytest>=7.0",
    "pytest-cov>=4.0",
    "black>=23.0",
    "flake8>=6.0",
    "mypy>=1.0",
    "pre-commit>=3.0",  # Add this
]
```

2. **Create `.pre-commit-config.yaml`** with the hooks you want

1. **Update CONTRIBUTING.md** with setup instructions

Would you like me to help set this up for your project?
