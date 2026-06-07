---
name: evalhub-discovery
description: "Use when discovering EvalHub providers, benchmarks, or collections — listing what evaluation options exist, filtering by capability (e.g. safety, reasoning), or reading agent metadata. Does NOT cover job submission or status monitoring."
user-invocable: false
---

# EvalHub Discovery Skill

Discover providers, benchmarks, and collections from the EvalHub API. All knowledge comes from the API at runtime — never hardcode IDs or names.

## Prerequisites

| Variable | Purpose | Example |
|----------|---------|---------|
| `EVALHUB_BASE_URL` | EvalHub API base URL | `https://evalhub.apps.cluster.example.com` |
| `EVALHUB_TOKEN` | Bearer token for auth | `sha256~...` (from `oc whoami -t`) |
| `EVALHUB_TENANT` | Namespace / tenant | `eval-test` |

## Discovery Strategy

**Default starting point — two parallel calls:**

```bash
uv run ~/.claude/skills/evalhub/scripts/evalhub_providers.py --agent 2>/dev/null
uv run ~/.claude/skills/evalhub/scripts/evalhub_collections.py --agent 2>/dev/null
```

The `--agent` output contains the **complete** agent metadata block for every provider/collection. Do not fetch individual providers afterwards — everything is already here.

**Filter when user intent is clear:**

```bash
uv run ~/.claude/skills/evalhub/scripts/evalhub_providers.py --target-type agent 2>/dev/null
uv run ~/.claude/skills/evalhub/scripts/evalhub_providers.py --evaluates safety 2>/dev/null
uv run ~/.claude/skills/evalhub/scripts/evalhub_collections.py --evaluates safety 2>/dev/null
```

**Single provider (only when user explicitly asks for benchmarks):**

```bash
uv run ~/.claude/skills/evalhub/scripts/evalhub_providers.py PROVIDER_ID 2>/dev/null
```

## MCP Mode (preferred)

When `evalhub` MCP server is connected, use resources instead of Python scripts:

| MCP Resource URI | Replaces |
|------------------|---------|
| `evalhub://providers` | `evalhub_providers.py --agent` |
| `evalhub://providers/{id}` | `evalhub_providers.py PROVIDER_ID` |
| `evalhub://benchmarks` | `evalhub_providers.py --benchmarks` |
| `evalhub://benchmarks?label=safety` | `evalhub_providers.py --evaluates safety` |
| `evalhub://collections` | `evalhub_collections.py --agent` |
| `evalhub://collections/{id}` | `evalhub_collections.py COLLECTION_ID` |

## Agent Metadata Fields

| Field | How to use |
|-------|-----------|
| `evaluates` | Match against user intent — "safety" → `--evaluates safety` |
| `target_type` | `model`, `agent`, or `inference_server` |
| `summary` | Present to the user |
| `recommended_when` | When to suggest this provider/collection |
| `hints` | Constructing valid job requests — read before submitting |
| `result_interpretation` | How to explain scores after a run |
| `complements` | Suggest follow-up evaluations |

## Commands

### Providers

```bash
uv run ~/.claude/skills/evalhub/scripts/evalhub_providers.py                   # summary
uv run ~/.claude/skills/evalhub/scripts/evalhub_providers.py --agent           # full metadata
uv run ~/.claude/skills/evalhub/scripts/evalhub_providers.py PROVIDER_ID       # single provider
uv run ~/.claude/skills/evalhub/scripts/evalhub_providers.py --target-type model
uv run ~/.claude/skills/evalhub/scripts/evalhub_providers.py --evaluates safety
```

### Benchmarks

```bash
uv run ~/.claude/skills/evalhub/scripts/evalhub_providers.py --benchmarks
uv run ~/.claude/skills/evalhub/scripts/evalhub_providers.py --benchmarks --provider PROVIDER_ID
uv run ~/.claude/skills/evalhub/scripts/evalhub_providers.py --benchmarks --category CATEGORY
```

### Collections

```bash
uv run ~/.claude/skills/evalhub/scripts/evalhub_collections.py                  # summary
uv run ~/.claude/skills/evalhub/scripts/evalhub_collections.py --agent          # full metadata
uv run ~/.claude/skills/evalhub/scripts/evalhub_collections.py COLLECTION_ID    # single
uv run ~/.claude/skills/evalhub/scripts/evalhub_collections.py --evaluates CAPABILITY
```

## Recommendations

- Prefer **collections** for broad user intents ("evaluate safety", "assess my model")
- Use **individual benchmarks** only when the user names one specifically or wants a quick single-benchmark run
- Collections have curated weights and pass thresholds — prefer them for comprehensive assessments
- Always discover first — never assume an ID exists without checking
