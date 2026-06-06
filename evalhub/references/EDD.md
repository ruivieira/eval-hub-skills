# Evaluation-Driven Development (EDD)

EDD is the AI equivalent of Test-Driven Development (TDD). Instead of writing tests before code, you define evaluation criteria before deploying or fine-tuning a model. The cycle ensures model quality is measurable and improvable.

## The EDD Cycle

```
Define Criteria --> Measure Scores --> Iterate
      ^                                   |
      |___________________________________|
```

### Phase 1: Define Criteria

Discover the right evaluations for the user's goals using agent metadata from the API.

**Discovery steps:**

1. Match the user's intent to `evaluates` tags:
   ```bash
   uv run scripts/evalhub_providers.py --evaluates safety --agent
   uv run scripts/evalhub_collections.py --evaluates safety --agent
   ```

2. Filter by target type if you know what the user is evaluating:
   ```bash
   uv run scripts/evalhub_providers.py --target-type agent --agent
   uv run scripts/evalhub_providers.py --target-type model --agent
   ```

3. Read `recommended_when` from the provider's agent metadata to confirm the match

4. Check `hints` for operational requirements (model naming, secrets, parameters)

**Setting thresholds:**
- Read `result_interpretation` from the provider/collection to understand metric baselines
- Use `score_ranges` (when available on benchmarks) to understand what "good" looks like
- Start conservatively; tighten as the model improves
- Use `--num-examples 10` for fast iteration on threshold calibration

### Phase 2: Measure Scores

Run the evaluation and use agent metadata to interpret results.

```bash
# Submit using provider/benchmark IDs discovered in Phase 1
uv run scripts/evalhub_eval.py \
  --model-url http://model:8000/v1 --model-name my-model \
  --provider PROVIDER_ID \
  --benchmark BENCHMARK_ID \
  --threshold 0.7 \
  --tag "edd-iteration-1" \
  --experiment-name "my-model-edd"

# Or use a collection
uv run scripts/evalhub_eval.py \
  --model-url http://model:8000/v1 --model-name my-model \
  --collection COLLECTION_ID \
  --tag "edd-iteration-1" \
  --experiment-name "my-model-edd"

# Wait for results
uv run scripts/evalhub_status.py JOB_ID --wait
```

**Interpreting results using agent metadata:**
- Read the provider's `result_interpretation` for metric direction and baselines
- Read the benchmark's `result_interpretation` for benchmark-specific guidance
- Check `score_ranges` to map scores to semantic meanings
- Key result fields: `results.test.pass`, `results.test.score`, `results.benchmarks[].metrics`, `results.mlflow_experiment_url`

### Phase 3: Iterate

If thresholds are not met, improve the model and re-evaluate.

**Iteration strategies:**
1. **Prompt engineering** — adjust system prompts, few-shot examples
2. **Fine-tuning** — additional training on domain-specific data
3. **Model selection** — try a different base model
4. **RAG improvements** — better retrieval, re-ranking, chunking

**Suggest complementary evaluations:**
After running one provider, read its `complements` field to suggest what to run next.

**Track iterations with tags and experiments:**

```bash
uv run scripts/evalhub_eval.py \
  --model-url http://model:8000/v1 --model-name my-model \
  --provider PROVIDER_ID --benchmark BENCHMARK_ID \
  --threshold 0.7 --tag "edd-iteration-2" \
  --experiment-name "my-model-edd"
```

Tags and experiment names let you compare runs in MLflow.

## EDD Patterns

### Pattern: Safety Gate

Run safety evaluations before any deployment:

```bash
# Discover safety providers and collections
uv run scripts/evalhub_providers.py --evaluates safety --agent
uv run scripts/evalhub_collections.py --evaluates safety --agent

# Run a safety collection or individual safety benchmarks
uv run scripts/evalhub_eval.py \
  --model-url http://model:8000/v1 --model-name my-model \
  --collection SAFETY_COLLECTION_ID \
  --tag "safety-gate"
```

If the safety gate fails, block deployment.

### Pattern: Regression Check

Re-run the same evaluations after model changes to catch regressions:

```bash
# Baseline
uv run scripts/evalhub_eval.py \
  --model-url http://model:8000/v1 --model-name my-model-v1 \
  --provider PROVIDER_ID --benchmark BENCHMARK_ID \
  --tag "baseline" --experiment-name "regression-check"

# After changes
uv run scripts/evalhub_eval.py \
  --model-url http://model:8000/v1 --model-name my-model-v2 \
  --provider PROVIDER_ID --benchmark BENCHMARK_ID \
  --tag "post-change" --experiment-name "regression-check"
```

Compare results in MLflow.

### Pattern: Collection-Based Evaluation

Use curated collections for standardised evaluation suites:

```bash
# Discover collections
uv run scripts/evalhub_collections.py --agent

# Run a collection
uv run scripts/evalhub_eval.py \
  --model-url http://model:8000/v1 --model-name my-model \
  --collection COLLECTION_ID \
  --tag "collection-run"
```

### Pattern: Quick Iteration

Use `--num-examples` to run a small subset during development:

```bash
# Fast: 10 examples per benchmark (~seconds)
uv run scripts/evalhub_eval.py \
  --model-url http://model:8000/v1 --model-name my-model \
  --provider PROVIDER_ID --benchmark BENCHMARK_ID \
  --num-examples 10 --tag "dev-quick"
```

### Pattern: Agent Evaluation

When evaluating agentic systems with tool calling:

```bash
# Discover agent-focused providers
uv run scripts/evalhub_providers.py --target-type agent --agent

# Run using discovered provider and benchmark IDs
uv run scripts/evalhub_eval.py \
  --model-url http://model:8000/v1 --model-name my-agent \
  --provider AGENT_PROVIDER_ID --benchmark BENCHMARK_ID \
  --tag "agent-security"
```

## Context-Aware Recommendations

Always discover recommendations dynamically from the API. Never assume which providers or benchmarks exist.

```bash
# Discover by capability
uv run scripts/evalhub_providers.py --evaluates safety --agent
uv run scripts/evalhub_providers.py --evaluates reasoning --agent
uv run scripts/evalhub_providers.py --evaluates throughput --agent

# Discover by target type
uv run scripts/evalhub_providers.py --target-type model --agent
uv run scripts/evalhub_providers.py --target-type agent --agent
uv run scripts/evalhub_providers.py --target-type inference_server --agent

# Discover collections by capability
uv run scripts/evalhub_collections.py --evaluates safety --agent
uv run scripts/evalhub_collections.py --evaluates general --agent
```

Read the `recommended_when` field on each provider/collection to match against the user's situation.
