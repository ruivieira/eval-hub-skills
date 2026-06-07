---
name: evalhub-eval
description: "Use when submitting an evaluation job to EvalHub — running a model against benchmarks or collections. Covers job creation only. For status monitoring, use evalhub-jobs. For provider/benchmark discovery, use evalhub-discovery."
user-invocable: false
---

# EvalHub Eval Submission Skill

Submit evaluation jobs to EvalHub. Always discover providers and benchmarks first (use evalhub-discovery) before constructing a submission.

## Prerequisites

| Variable | Purpose | Example |
|----------|---------|---------|
| `EVALHUB_BASE_URL` | EvalHub API base URL | `https://evalhub.apps.cluster.example.com` |
| `EVALHUB_TOKEN` | Bearer token for auth | `sha256~...` (from `oc whoami -t`) |
| `EVALHUB_TENANT` | Namespace / tenant | `eval-test` |

## Rules

- **Discover first** — never submit with hardcoded IDs; list providers/collections first
- **Read `hints`** in the provider's agent metadata before constructing the request
- **Use `--dry-run`** to inspect the request JSON before submitting, especially for new benchmarks
- **Suppress stderr** — append `2>/dev/null` to all script calls

## MCP Mode (preferred)

When `evalhub` MCP server is connected, call the `submit_evaluation` tool instead of running the script:

```
submit_evaluation(
  model_url="http://model-server:8000/v1",
  model_name="my-model",
  provider_id="PROVIDER_ID",
  benchmark_ids=["BENCHMARK_ID"],
  # or: collection_id="COLLECTION_ID"
)
```

After submitting, save the returned job ID with state.py before anything else:

```bash
uv run ~/.claude/skills/evalhub/scripts/state.py set job_id JOB_ID 2>/dev/null
```

## Script Usage

### With benchmarks

```bash
uv run ~/.claude/skills/evalhub/scripts/evalhub_eval.py \
  --model-url http://model-server:8000/v1 \
  --model-name my-model \
  --provider PROVIDER_ID \
  --benchmark BENCHMARK_ID \
  2>/dev/null
```

### With a collection

```bash
uv run ~/.claude/skills/evalhub/scripts/evalhub_eval.py \
  --model-url http://model-server:8000/v1 \
  --model-name my-model \
  --collection COLLECTION_ID \
  2>/dev/null
```

### From a JSON file

```bash
uv run ~/.claude/skills/evalhub/scripts/evalhub_eval.py --json request.json 2>/dev/null
```

### Dry run (inspect request without submitting)

```bash
uv run ~/.claude/skills/evalhub/scripts/evalhub_eval.py \
  --dry-run \
  --model-url http://model-server:8000/v1 \
  --model-name my-model \
  --provider PROVIDER_ID \
  --benchmark BENCHMARK_ID \
  2>/dev/null
```

## Optional Flags

| Flag | Purpose |
|------|---------|
| `--name TEXT` | Job name (auto-generated if omitted) |
| `--tag TEXT` | Tag (repeatable) |
| `--num-examples N` | Limit to N examples per benchmark — use for quick iteration |
| `--threshold 0.7` | Pass/fail threshold |
| `--experiment-name TEXT` | MLflow experiment name |
| `--queue TEXT` | Kueue queue name |
| `--model-secret TEXT` | Kubernetes secret name for model auth |
| `--dry-run` | Print the request JSON without submitting |

## After Submitting

The script prints the job object as JSON including the job ID. Always:

1. Extract the job ID from the output
2. Save it: `uv run ~/.claude/skills/evalhub/scripts/state.py set job_id JOB_ID 2>/dev/null`
3. Use evalhub-jobs to monitor status
