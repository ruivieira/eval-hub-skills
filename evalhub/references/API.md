# EvalHub API Reference

Base path: `/api/v1`

All endpoints (except health and OpenAPI) require:
- `Authorization: Bearer <token>` header
- `X-Tenant: <namespace>` header

## Health

### GET /api/v1/health

Check service health. No auth required.

**Response**: `{"status": "ok", "build": "...", "build_date": "..."}`

## Providers

### GET /api/v1/evaluations/providers

List all registered evaluation providers.

**Query parameters**:
- `scope` (optional): Filter scope
- `benchmarks` (optional): Include benchmark details

**Response**:
```json
{
  "items": [
    {
      "resource": {"id": "provider-id", "created_at": "..."},
      "name": "Provider Name",
      "title": "Provider Title",
      "description": "...",
      "agent": {
        "evaluates": ["capability-1", "capability-2"],
        "recommended_when": ["When to recommend this provider"],
        "target_type": "model",
        "summary": "Concise description for agent tool listings",
        "complements": ["other-provider-id"],
        "hints": ["Operational guidance for constructing requests"],
        "result_interpretation": ["How to interpret scores from this provider"]
      },
      "benchmarks": [
        {
          "id": "benchmark-id",
          "name": "Benchmark Name",
          "category": "category",
          "metrics": ["metric_1", "metric_2"],
          "primary_score": {"metric": "metric_1", "lower_is_better": false},
          "pass_criteria": {"threshold": 0.5},
          "agent": {
            "result_interpretation": "Benchmark-specific score interpretation guidance."
          }
        }
      ]
    }
  ],
  "limit": 100,
  "total_count": 4
}
```

### GET /api/v1/evaluations/providers/{provider_id}

Get a single provider with its benchmarks.

### POST /api/v1/evaluations/providers

Create a new provider.

### PUT /api/v1/evaluations/providers/{provider_id}

Replace a provider.

### PATCH /api/v1/evaluations/providers/{provider_id}

Partial update of a provider.

### DELETE /api/v1/evaluations/providers/{provider_id}

Delete a provider.

## Collections

### GET /api/v1/evaluations/collections

List all benchmark collections.

**Response**:
```json
{
  "items": [
    {
      "resource": {"id": "collection-id"},
      "name": "Collection Name",
      "description": "Collection description",
      "category": "category",
      "agent": {
        "evaluates": ["capability-1", "capability-2"],
        "recommended_when": ["When to recommend this collection"],
        "summary": "Concise description for agent tool listings",
        "complements": ["other-collection-or-provider-id"],
        "hints": ["Operational guidance for running this collection"],
        "result_interpretation": ["How to interpret the aggregate score"]
      },
      "benchmarks": [...]
    }
  ]
}
```

### GET /api/v1/evaluations/collections/{collection_id}

Get a single collection with its benchmarks.

### POST /api/v1/evaluations/collections

Create a collection.

**Request body**:
```json
{
  "name": "my-collection",
  "description": "Custom benchmark suite",
  "category": "safety",
  "benchmarks": [
    {"id": "benchmark-id", "provider_id": "provider-id", "weight": 1.0}
  ]
}
```

### PUT /api/v1/evaluations/collections/{collection_id}

Replace a collection.

### PATCH /api/v1/evaluations/collections/{collection_id}

Partial update.

### DELETE /api/v1/evaluations/collections/{collection_id}

Delete a collection.

## Evaluation Jobs

### POST /api/v1/evaluations/jobs

Create an evaluation job.

**Request body**:
```json
{
  "name": "my-evaluation",
  "description": "optional description",
  "model": {
    "url": "http://model-server:8000/v1",
    "name": "model-name",
    "auth": {
      "secret_ref": "k8s-secret-name"
    },
    "parameters": {
      "temperature": 0.0,
      "max_tokens": 256
    }
  },
  "benchmarks": [
    {
      "id": "benchmark-id",
      "provider_id": "provider-id",
      "parameters": {"num_examples": 10},
      "pass_criteria": {"threshold": 0.7},
      "primary_score": {"metric": "metric_name", "lower_is_better": false}
    }
  ],
  "collection": {
    "id": "collection-id"
  },
  "tags": ["experiment-v1"],
  "experiment": {
    "name": "my-experiment",
    "tags": [{"key": "team", "value": "ml-platform"}]
  },
  "pass_criteria": {
    "threshold": 0.7
  },
  "queue": {
    "kind": "kueue",
    "name": "eval-queue"
  },
  "exports": {
    "oci": {
      "coordinates": {
        "oci_host": "quay.io",
        "oci_repository": "org/eval-results",
        "oci_tag": "v1"
      },
      "k8s": {
        "connection": "registry-credentials"
      }
    }
  }
}
```

**Notes**:
- Either `benchmarks` or `collection` must be provided (not both).
- `model.url` must be an OpenAI-compatible inference endpoint.
- `model.auth.secret_ref` references a Kubernetes secret with the model API key.
- `parameters` on benchmarks are provider-specific (e.g. `num_examples` for lm-eval).
- `queue` is optional; when provided, the job is submitted to a Kueue queue.

**Response**: `EvaluationJobResource` (see below).

### GET /api/v1/evaluations/jobs

List evaluation jobs.

**Query parameters**:
- `status_filter` (optional): `pending`, `running`, `completed`, `failed`, `cancelled`, `partially_failed`
- `limit` (optional): Max results (default: 100)
- `name` (optional): Filter by name
- `tags` (optional): Filter by tags

**Response**:
```json
{
  "items": [...],
  "limit": 100,
  "total_count": 5
}
```

### GET /api/v1/evaluations/jobs/{job_id}

Get a single job with status and results.

**Response** (`EvaluationJobResource`):
```json
{
  "resource": {
    "id": "job-uuid",
    "created_at": "2026-04-27T10:00:00Z",
    "mlflow_experiment_id": "123"
  },
  "name": "my-evaluation",
  "model": {"url": "...", "name": "..."},
  "benchmarks": [...],
  "status": {
    "state": "completed",
    "message": {"message": "All benchmarks completed"},
    "benchmarks": [
      {
        "provider_id": "provider-id",
        "id": "benchmark-id",
        "benchmark_index": 0,
        "status": "completed",
        "started_at": "...",
        "completed_at": "..."
      }
    ]
  },
  "results": {
    "benchmarks": [
      {
        "id": "benchmark-id",
        "provider_id": "provider-id",
        "benchmark_index": 0,
        "metrics": {"metric_1": 0.85, "metric_2": 0.82},
        "mlflow_run_id": "run-uuid",
        "test": {
          "primary_score": 0.82,
          "primary_score_metric": "metric_2",
          "threshold": 0.7,
          "pass": true
        }
      }
    ],
    "test": {
      "score": 0.82,
      "threshold": 0.7,
      "pass": true
    },
    "mlflow_experiment_url": "https://mlflow.example.com/..."
  }
}
```

### DELETE /api/v1/evaluations/jobs/{job_id}

Cancel a running job or delete a completed one.

**Query parameters**:
- `hard_delete` (optional): `true` to permanently delete instead of cancel

### POST /api/v1/evaluations/jobs/{job_id}/events

Update benchmark status (used by job runtimes, not end users).

### GET /api/v1/evaluations/jobs/{job_id}/logs

Get job execution logs.

**Query parameters**:
- `offset` (optional): Byte offset to start reading from

**Response**:
```json
{
  "job_id": "job-uuid",
  "content": "log output...",
  "offset": 0,
  "has_more": false,
  "source": "pod",
  "total_bytes": 1234
}
```

## Job States

| State | Description |
|-------|-------------|
| `pending` | Job created, waiting to be scheduled |
| `running` | Job is executing benchmarks |
| `completed` | All benchmarks finished successfully |
| `failed` | Job failed (check `status.message` for details) |
| `cancelled` | Job was cancelled by user |
| `partially_failed` | Some benchmarks completed, some failed |

## Pagination

List endpoints return paginated responses:

```json
{
  "items": [...],
  "first": "/api/v1/evaluations/jobs?limit=100",
  "next": "/api/v1/evaluations/jobs?limit=100&offset=100",
  "limit": 100,
  "total_count": 250
}
```

## OpenAPI Specification

### GET /openapi.yaml

Returns the full OpenAPI 3.1.0 specification in YAML format.
