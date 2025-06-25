# Developer Guidelines

This repository uses a number of automated checks and tools.
Follow these guidelines when contributing.

## Set Up

- Install development dependencies with `pip install --upgrade hatch`.

## Coding style

- Format code using **black**. The `review.yml` workflow automatically
  formats and suggests changes.
- Write docstrings in **NumPy** style. `pydocstyle` is run via
  the `lint-docstrings.yml` workflow.
- Type annotations are required and checked with **mypy** via `lint-types.yml`.
- Ensure spelling with **codespell** (`lint-spelling.yml`).

## Tests and Checks

- Run the full test suite with `hatch run cov`.
- Run linting checks with `hatch run lint`
- If environments become stale use `hatch env prune` and `hatch env show --ascii`.

## Continuous Integration

- Continuous integration is performed via GitHub actions
- GitHub Actions run tests (`test.yml`) on Python 3.10–3.12 using Hatch.
- Additional workflows lint commit messages
  (`commitlint.yml`) and pull request titles (`lint-pr.yml`).
- Documentation is deployed via `deploy-docs.yml` on pushes to `main`.
- Semantic releases are handled via `release.yml`.

## Documentation

- Documentation is generated with **mkdocs** using the `mkdocs-material`
  theme and `mkdocstrings` with NumPy docstring style (see `mkdocs.yml`).

## Expectations for Pull Requests

- Adhere to Conventional Commits for commit messages and PR titles.
- Provide thorough NumPy-style docstrings similar to those
  found in `conversations/_conversations.py`.
- Add or update tests in the `tests` directory for any code changes.
- Run `hatch run cov` and `hatch run lint` and ensure
  all tests and linting pass before committing.
