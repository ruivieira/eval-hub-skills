# Evaluation Scenarios

Each scenario is a pair of files:
- `<name>/input.yaml` — the user prompt and context
- `<name>/expected.yaml` — the expected agent behaviour

Use these to verify skill guidance produces the right outcomes.

## Running

```bash
# Manual review — compare actual vs expected
cat eval/01-list-providers/input.yaml
cat eval/01-list-providers/expected.yaml
```

## Scenarios

| # | Name | Skill | Description |
|---|------|-------|-------------|
| 01 | list-providers | evalhub-discovery | Discover all providers with agent metadata |
| 02 | filter-by-evaluates | evalhub-discovery | Filter providers by a capability tag |
| 03 | select-collection | evalhub-discovery | Choose the right collection for a user's intent |
| 04 | submit-benchmark | evalhub-eval | Submit a job with individual benchmarks |
| 05 | submit-collection | evalhub-eval | Submit a job using a collection |
| 06 | dry-run | evalhub-eval | Inspect request JSON before submitting |
| 07 | check-status | evalhub-jobs | Get status of a running job |
| 08 | wait-for-completion | evalhub-jobs | Poll until a job reaches terminal state |
| 09 | cancel-job | evalhub-jobs | Cancel a running job |
| 10 | edd-cycle | evalhub | Full EDD cycle: discover → submit → interpret |
