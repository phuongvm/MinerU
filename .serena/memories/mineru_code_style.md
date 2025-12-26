# Code Style and Conventions

*   **Language:** Python (3.10+)
*   **Formatting:** The project likely follows `ruff` or `black` formatting styles (standard 4-space indentation).
*   **Type Hinting:** Use Python type hints (e.g., `def func(arg: str) -> bool:`) where possible, especially in new code.
*   **Docstrings:** Use docstrings for modules, classes, and functions to explain purpose and arguments.
*   **Logging:** Use `loguru` for logging instead of the standard `logging` module.
    ```python
    from loguru import logger
    logger.info("Message")
    logger.error("Error")
    ```
*   **Path Handling:** Use `pathlib.Path` for file path manipulations instead of `os.path` where feasible.
*   **Configuration:** Configuration is handled via environment variables (e.g., `MINERU_MODEL_SOURCE`) and config files (`magic-pdf.json` / `mineru.json`).
*   **Imports:** Group imports: standard library, third-party, local application (relative or absolute `mineru...`).
*   **Device Handling:** Use `mineru.utils.config_reader.get_device()` to ensure compatibility across CUDA, MPS, and CPU.
