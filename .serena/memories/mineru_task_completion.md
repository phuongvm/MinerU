# Task Completion Checklist

After completing a task in the MinerU project:

1.  **Verification:**
    *   Run relevant unit tests: `pytest tests/unittest/test_e2e.py` (or specific tests related to changes).
    *   If functionality involves PDF parsing, verify the output (Markdown/JSON) manually or via provided visualization tools if applicable.
    *   Ensure no regressions in the default `pipeline` backend.

2.  **Code Quality:**
    *   Run linters/formatters: `ruff check .` and `ruff format .`.
    *   Ensure no unused imports or variables.

3.  **Documentation:**
    *   Update `README.md` or specific docs in `docs/` if new features or configuration options are added.
    *   Add docstrings to new functions/classes.

4.  **Dependencies:**
    *   If new dependencies are added, update `pyproject.toml`.

5.  **Commit:**
    *   Write a clear, concise commit message explaining *why* the change was made.
