---
description: "Python development guidelines."
applyTo: "**/*.py,**/pyproject.toml"
---

# Python development guidelines

- **Strict Typing & Docstrings:** ALWAYS add type hints (including return types) and PEP 257 compliant docstrings to all functions and classes.
- **Modern Python Features:** Use modern Python features up to 3.12.
- **Doc Strings**: The doc strings should be in the format of Google style. Always leave a blank line after doc strings.
- **Testing**: Write unit tests for important functions and classes. Use `pytest` as the testing framework.
- **Miscellaneous**
    - Use `is` for identity checks and `==` for equality checks.
    - Use f-strings for string formatting.
    - Use `with` statements for file operations.
    - Use list comprehensions where appropriate.
    - Use double quotes for strings.
    - Use `_ is None` and `_ is not None` for `None` checks.
