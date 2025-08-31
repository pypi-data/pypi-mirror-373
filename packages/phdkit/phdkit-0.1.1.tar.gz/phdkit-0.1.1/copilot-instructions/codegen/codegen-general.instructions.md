---
description: "General coding guidelines."
applyTo: "**"
---

# Best coding practices

- **Modular Design:** Emphasize clear separation of concerns.
- **Preserve Comments:** Existing comments in code must be retained.
- Tables and columns in databases should use CamelCase, including those one-word names.
- Remember to refer to the library/package/tool documentation provided by the Context7 MCP if necessary and available. Note that I frequently use the following private libraries/packages without docs on the Context7 server, for which you should refer to their source code instead:
  - `phdkit`
- **Python Dependency Management:** (VERY IMPORTANT!) Utilize `uv` and virtual environments. All code and scripts must be executed via `uv run <main_command> <subcommand>`. Otherwise, a `python -m <main_command_module> <subcommand>` is expected to produce a module import error. Besides, `uv run python -m <main_command_module> <subcommand>` will likely cause problems too. For example, if the main command module is in the directory `src/cmd`, you should run it as `uv run cmd <subcommand>`. Similarly, use `uv run pytest` to run `pytest` unit tests. DON'T USE `python -m cmd` or `python -m src/cmd` to run the module!
