## Commands
- **Run**: `poe run` or `rovr`
- **Build**: `uv build`
- **Dev Mode**: `poe dev` (hot reload)
- **Logs**: `poe log` (when in dev mode)
- **Schema Gen**: `poe gen-schema` (for docs, when the `schema.json` changes)
- **Lint**: `ruff check` (errors), `ruff format` (fix)
- **Type Check**: `uvx ty check . --ignore unresolved-import`
- **Pre-commit**: `pre-commit run --all-files`

## Code Style
- **Python 3.13+**
- **Imports**: Group stdlib/third-party/local (ruff)
- **Formatting**: Double quotes, f-strings (ruff)
- **Types**: Mandatory annotations (ty-enforced)
- **Naming**: `snake_case`, `PascalCase`
- **Paths**: `path.join()` always (use `utils.normalise` where necessary)
- **Errors**: `contextlib.suppress` for specific cases
- **Patterns**: Prefer `match/case` over `if-elif`
- **Docs**: Docstrings (DOC rules)
- **Config**: TOML format
- **UI**: Textual TUI framework
