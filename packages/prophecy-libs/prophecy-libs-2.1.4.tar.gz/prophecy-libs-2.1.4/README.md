# prophecy-python-libs

## To run Ruff linting rules locally:
- Read about rules: https://docs.astral.sh/ruff/rules/
- For this repo, the rules are configured in pyproject.toml file
- To install ruff: (`$ pip install -r requirements.txt`)
- To run check command: (`$ ruff check <dir/files>`)

## To run Ruff check as a pre-commit hook:
- To install pre-commit: (`$ pip install -r requirements.txt`)
- To set up pre-commit hook locally: (`$ pre-commit install`)
- To run `ruff check` manually only on the changed files (`$ pre-commit run`)
- To skip pre-commit hooks during a git commit (`$ git commit --no-verify`)