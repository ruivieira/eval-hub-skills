---
name: evalhub-jobs
description: "Use when monitoring, waiting on, cancelling, or fetching logs for an EvalHub evaluation job. Covers the full job lifecycle after submission. For submitting new jobs, use evalhub-eval."
user-invocable: false
---

# EvalHub Jobs Skill

Monitor, poll, cancel, and fetch logs for EvalHub evaluation jobs.

## Prerequisites

| Variable | Purpose | Example |
|----------|---------|---------|
| `EVALHUB_BASE_URL` | EvalHub API base URL | `https://evalhub.apps.cluster.example.com` |
| `EVALHUB_TOKEN` | Bearer token for auth | `sha256~...` (from `oc whoami -t`) |
| `EVALHUB_TENANT` | Namespace / tenant | `eval-test` |

## Job States

`pending` → `running` → `completed` | `failed` | `cancelled` | `partially_failed`

## MCP Mode (preferred)

When `evalhub` MCP server is connected:

| MCP Tool | Replaces |
|----------|---------|
| `get_job_status` | `evalhub_status.py JOB_ID` |
| `cancel_job` | `evalhub_status.py JOB_ID --cancel` |

MCP resources for listing:

| MCP Resource URI | Replaces |
|------------------|---------|
| `evalhub://jobs` | `evalhub_status.py --list` |
| `evalhub://jobs?status=running` | `evalhub_status.py --list --status running` |
| `evalhub://jobs/{id}` | `evalhub_status.py JOB_ID` |

## Polling Strategy

Evaluation jobs can take minutes to hours. Choose the right approach:

| Situation | Approach |
|-----------|---------|
| Short job (< 5 min expected) | `--wait --timeout 300` or MCP `get_job_status` loop |
| Long job (> 5 min) | MCP `get_job_status` every 30s; show progress updates |
| Context compression risk | Save job ID with `state.py`, recover on next session |
| Job already running | Check `state.py status` first — job ID may already be saved |

When polling via MCP, stop when state is `completed`, `failed`, `cancelled`, or `partially_failed`.

## Commands

### Check single job status

```bash
uv run ~/.claude/skills/evalhub/scripts/evalhub_status.py JOB_ID 2>/dev/null
```

### Wait for completion (blocking)

```bash
uv run ~/.claude/skills/evalhub/scripts/evalhub_status.py JOB_ID --wait 2>/dev/null
uv run ~/.claude/skills/evalhub/scripts/evalhub_status.py JOB_ID --wait --timeout 1800 2>/dev/null
```

### List jobs

```bash
uv run ~/.claude/skills/evalhub/scripts/evalhub_status.py --list 2>/dev/null
uv run ~/.claude/skills/evalhub/scripts/evalhub_status.py --list --status running 2>/dev/null
uv run ~/.claude/skills/evalhub/scripts/evalhub_status.py --list --status pending 2>/dev/null
```

### Cancel a job

```bash
uv run ~/.claude/skills/evalhub/scripts/evalhub_status.py JOB_ID --cancel 2>/dev/null
```

### Get job logs

```bash
uv run ~/.claude/skills/evalhub/scripts/evalhub_logs.py JOB_ID 2>/dev/null
```

## State Persistence

Before polling a long-running job, save the job ID to survive context compression:

```bash
uv run ~/.claude/skills/evalhub/scripts/state.py set job_id JOB_ID 2>/dev/null
```

On session resume, check for in-flight jobs:

```bash
uv run ~/.claude/skills/evalhub/scripts/state.py status 2>/dev/null
```

Clear after a job reaches a terminal state:

```bash
uv run ~/.claude/skills/evalhub/scripts/state.py set job_id "" 2>/dev/null
```

## Interpreting Results

After `completed`, read the provider's agent metadata for context:

```bash
uv run ~/.claude/skills/evalhub/scripts/evalhub_providers.py PROVIDER_ID 2>/dev/null
```

Use `agent.result_interpretation` to explain metric direction and baselines. Use `agent.complements` to suggest follow-up evaluations.

## Gotchas

- **Token expiry**: 401 errors mean the token expired — ask the user to run `oc whoami -t`
- **Long timeouts**: Default `--wait` timeout is 600s. Use `--timeout 3600` for heavy benchmarks
- **`num_examples`**: Jobs submitted with `--num-examples` run faster — check the submission parameters
