# Changelog

## [0.2.0] — unreleased

### Added
- Three focused sub-skills: `evalhub-discovery`, `evalhub-eval`, `evalhub-jobs`
- `evalhub/scripts/state.py` — key-value state persistence for long-running jobs (survives context compression)
- `AGENTS.md` — guidance for AI agents working on the plugin itself
- `.skillsaw.yaml` — skillsaw linter config with context budget thresholds
- `.claude/settings.json` — committed scoped permissions and `SessionStart` recovery hook
- `.mcp.json` — EvalHub MCP server registration via `EVALHUB_MCP_URL`
- MCP mode section in `evalhub/SKILL.md` with tool and resource mapping tables
- `--dry-run` flag on `evalhub_eval.py` — inspect request JSON without submitting
- `eval/` directory with 10 evaluation scenarios (input + expected pairs)
- Makefile targets: `install-all`, `uninstall-all`, `update-all`
- skillsaw added to `make lint`

### Changed
- `settings.local.json` simplified (permissions moved to committed `settings.json`)

## [0.1.0] — initial release

### Added
- `evalhub` skill with `SKILL.md` covering discovery, evaluation, and job lifecycle
- Python scripts: `evalhub_check.py`, `evalhub_collections.py`, `evalhub_eval.py`, `evalhub_logs.py`, `evalhub_providers.py`, `evalhub_status.py`
- References: `API.md`, `EDD.md`
- Assets: `eval-job-template.json`
- Makefile: `lint`, `test`, `install`, `uninstall`, `update`, `check`
- Unit tests (no live service required)
- CI: ruff, shellcheck
