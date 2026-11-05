# Token Economics — Module 3: Make the Cache Hit

**Taller Academy | Lab 3 (after Module 3)**

[Read the complete Lab 3 answer](SUBMISSION.md) · [Paper predictions](docs/EXPERIMENT_2_PAPER.md) · [Reproduction instructions](docs/HOW_TO_MEASURE.md)

This submission contains the five exercises and the wrap-up, using the course's **illustrative price sheet** (not live provider charges). All example workloads and documents are synthetic. No company secrets, customer records, API credentials, or proprietary policies are included.

## Lab coverage

1. Break-even calculations for no caching, 5-minute / 1-hour TTL, different arrival gaps, and no-write-premium provider. Both *sliding* TTL and *fixed absolute* TTL semantics are documented, since the source's stated 15-minute totals assume refresh-on-read.
2. Four specified cache experiments A/B/C/D, with **predictions made before measurement** and an explicitly labeled **paper version** (no API key). The optional SDK runner is in `src/experiments.py`; **no calls have been executed**.
3. Seven silent invalidators and a corrected request builder in `src/invalidators.py`.
4. Parallel versus warm-up sequencing versus 50%-discount batch, both with and without write premium.
5. Five explicitly illustrative workloads and a transparent monthly savings model.

For the baseline wrap-up, the earlier public Lab 1 Ollama example had one uncached 68-input-token request and 58 output tokens. An actual caching win cannot be inferred from one request, and no new baseline run is claimed.

## Files

- `SUBMISSION.md` — grading-ready written answers and four rubric categories.
- `src/pricing.py` — reusable pricing arithmetic and TTL interpretations.
- `src/experiments.py` and `src/provider.py` — optional paid real-provider exercise (not run).
- `src/invalidators.py` — before/after code for exercise 3.
- `src/batch_candidates.py` — sample workload classifications and estimate.
- `docs/EXPERIMENT_2_PAPER.md` — 12 predicted per-call normalized usage lines.
- `docs/HOW_TO_MEASURE.md` — optional verification instructions.

## Optional run — NOT performed

```bash
python -m pip install -r requirements.txt
# Create your own >5000-token document in doc.txt and configure your own API key
python -m src.experiments --provider openai --doc doc.txt
```

For privacy and cost control, *running* the experiment is deliberately opt-in. The exercise 2 numbers in this submission are paper calculations, not fabricated observations. Actual cache behavior depends on the provider, model, prefix, minimum cacheable length, TTL, and request concurrency.
