# Exercise 2 — Paper experiment predictions (no API calls made)

**Status:** Predictions and hypothetical normalized usage ONLY. Nothing below is measured usage. The course explicitly permits this paper track without an API key.

## Assumptions declared before any experiment

- DOC = 6,000 tokens; each question (including any changing suffix) = 20 uncached tokens for consistent arithmetic.
- Rate / 1M input tokens: uncached $2.00, cached $0.20, cache write $2.50 (1.25× input price).
- Cache-aware provider with a 5-minute lifetime that can cache the stable document prefix, beginning with the first write; calls are sequential, two seconds apart; no expiry during a three-call experiment.
- The 300-word shortened version in D is assumed to encode to **400** tokens. Real token count depends on text and tokenizer. It is below the assumed provider minimum.
- For experiment B, a changing timestamp precedes the entire document, so assume no reusable prefix hits. The timestamp's cost is approximated within the 20 dynamic tokens.
- In A/C, the first call creates a 6,000-token cache entry; subsequent calls reuse it. Variable question text is not reused.
- Actual caching can be best-effort; not every provider reports writes; different minimums and tokenization change real values.

## Prediction table (written before any real execution)

| Experiment | Call | Predict cached_input > 0? | Predict cache_write > 0? | Uncached input | Cache write | Cached input | Output | Predicted input cost |
|---|---:|---|---|---:|---:|---:|---:|---:|
| A — stable DOC | 1 | No | Yes | 20 | 6,000 | 0 | Unmeasured | $0.01504 |
| A — stable DOC | 2 | Yes | No | 20 | 0 | 6,000 | Unmeasured | $0.00124 |
| A — stable DOC | 3 | Yes | No | 20 | 0 | 6,000 | Unmeasured | $0.00124 |
| B — timestamp at front | 1 | No | Yes | 20 | 6,000 | 0 | Unmeasured | $0.01504 |
| B — timestamp at front | 2 | No | Yes | 20 | 6,000 | 0 | Unmeasured | $0.01504 |
| B — timestamp at front | 3 | No | Yes | 20 | 6,000 | 0 | Unmeasured | $0.01504 |
| C — timestamp at end | 1 | No | Yes | 20 | 6,000 | 0 | Unmeasured | $0.01504 |
| C — timestamp at end | 2 | Yes | No | 20 | 0 | 6,000 | Unmeasured | $0.00124 |
| C — timestamp at end | 3 | Yes | No | 20 | 0 | 6,000 | Unmeasured | $0.00124 |
| D — short prefix | 1 | No | No | 420 | 0 | 0 | Unmeasured | $0.00084 |
| D — short prefix | 2 | No | No | 420 | 0 | 0 | Unmeasured | $0.00084 |
| D — short prefix | 3 | No | No | 420 | 0 | 0 | Unmeasured | $0.00084 |

### Expected input-only totals

| Experiment | Predicted input cost | Interpretation |
|---|---:|---|
| A | **$0.01752** | Stable long prefix: one write followed by two hits. |
| B | **$0.04512** | Volatile timestamp invalidates the long prefix every time. |
| C | **$0.01752** | Dynamic time is after stable DOC; two cache hits expected. |
| D | **$0.00252** | Short instructions are not eligible for caching; cheap because the input is much smaller, not because of cache hits. |

The paper table uses four normalized input counters and explicitly leaves **output unmeasured** because the exercise asks for *input* costs, and output length is not supplied. Real API usage for each call is intentionally absent. For a no-write-premium provider, move `cache_write` counts into `uncached_input` and use $2.00/M instead of $2.50/M.

**Provider:** Hypothetical 1.25×-premium cache provider in the paper version; **cache writes:** assumed and reported in our model, *not* observed from an API. The optional OpenAI runner in `src/experiments.py` explicitly records cache_write=0 because OpenAI's Responses usage lacks a standalone cache-write counter.
