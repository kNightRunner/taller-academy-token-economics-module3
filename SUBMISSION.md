# Lab 3 — Make the Cache Hit

**Course:** Taller Academy, The End of Cheap Tokens · Module 3  
**Delivery:** Written answers + reproducible code. **No API calls, tests or experiments executed.** Exercise 2 uses the explicitly permitted **paper version**; all numbers there are modeled, not observed.  
**Price assumptions:** $2.00 / 1M uncached input, $10.00 / 1M output, $0.20 / 1M cached input, $2.50 / 1M cache writes with 1.25× premium; batch = 50% off where eligible.

## Exercise 1 — Break-even by hand

**Document = 20,000 tokens × 10 questions. Ignore output.** Per uncached read: 20,000 × $2 / 1,000,000 = **$0.040**; per cached read: 20,000 × $0.20 / 1,000,000 = **$0.004**.

| Scenario: ten calls within 5 minutes | Writes | Cache reads | Input cost | Saving vs no cache |
|---|---:|---:|---:|---:|
| No caching | — | — | **$0.400** | — |
| 5-min TTL, 1.25× write ($0.050/write) | 1 | 9 | **$0.050 + $0.036 = $0.086** | 78.5% |
| 1-hour TTL, 2× write ($0.080/write) | 1 | 9 | **$0.080 + $0.036 = $0.116** | 71.0% |

**Ten calls spaced 15 minutes apart (t = 0, 15, …, 135):**

- **No cache:** $0.400.
- **5-minute cache:** ten misses/writes = 10 × $0.050 = **$0.500**, worse than no caching.
- **1-hour cache:** under the *course's presumed sliding TTL* (cache expiry refreshed by every read), the first request writes ($0.080), followed by nine cached hits ($0.036), total **$0.116**; the 1-hour cache is then the cheapest option.

**Important TTL caveat:** With a *fixed absolute* 1-hour TTL (expiry is not refreshed by hits), the spaced calls produce three writes (t = 0, 60, 120) and seven hits: 3 × $0.080 + 7 × $0.004 = **$0.268**. This is still cheaper than no caching. The course's **$0.116** figure depends on different TTL semantics. Cache provider behavior must be verified before production assumptions.

**No write premium; 30-minute cache:**

- Within five minutes: one standard-price write at $0.040 + nine hits at $0.004 = **$0.076**.
- Spaced 15 minutes: under a *sliding 30-minute TTL*, one standard write + nine hits = **$0.076** (course expectation).
- With *fixed absolute 30-minute TTL*, writes at t = 0, 30, 60, 90, 120 (five writes), five hits: 5 × $0.040 + 5 × $0.004 = **$0.220**.

**Takeaway:** Minimize volatile prefixes and check both TTL semantics and traffic spacing. A premium on frequent cache writes can make caching more expensive than no cache.

## Exercise 2 — Watch it hit, then break it (paper track)

**Experiment mode:** The course's permitted paper alternative; no API key provided, and no real provider calls made. **All per-call predictions were specified before measurement**, and there are **no observations**. See [complete 12-call normalized usage prediction table](docs/EXPERIMENT_2_PAPER.md).

Assume a 6,000-token cacheable DOC, 20 new uncached tokens per question, a 1.25× write premium, and that calls 2 and 3 in the stable-prefix cases arrive before expiry. For the `300`-word short-prefix case, assume 400 tokens (a paper approximation, not a counted token number).

| Experiment | Predicted call 1 | Predicted call 2 | Predicted call 3 | Total input cost | What would happen |
|---|---|---|---|---:|---|
| A — stable DOC | 6,000 write + 20 uncached | 6,000 cached + 20 uncached | 6,000 cached + 20 uncached | **$0.01752** | A reusable large prefix produces two expected hits. |
| B — timestamp before DOC | 6,000 write + 20 uncached | 6,000 write + 20 uncached | 6,000 write + 20 uncached | **$0.04512** | Changing the prefix head invalidates reuse. |
| C — timestamp after DOC | 6,000 write + 20 uncached | 6,000 cached + 20 uncached | 6,000 cached + 20 uncached | **$0.01752** | Variable material at the end preserves the reusable prefix. |
| D — prefix below minimum | 420 uncached | 420 uncached | 420 uncached | **$0.00252** | No hit: the shortened prompt is ineligible to cache. |

**Provider:** hypothetical premium-write provider, not a live API. **Writes reported:** modeled, not observed. **Actual normalized usage:** not available because the paper path does not involve real calls; the exact predicted normalized fields (`uncached_input`, `cache_write`, `cached_input`, `output`) for each of all 12 calls are in the linked table. This fulfills the supplied paper alternative, without misrepresenting simulated counts as measurements.

**Limitations:** Question/timestamp tokens are approximated at 20 dynamic tokens; actual output is unmeasured and excluded from this input-cost analysis. Production token counts and cache hits depend on tokenizer, model minimum, stable prefix, cache policy, and provider. Stable-prefix caching is not guaranteed.

## Exercise 3 — Spot the silent invalidators

| # | Cache problem | Why it breaks / wastes cache | Fix |
|---:|---|---|---|
| 1 | `user.enabled_tools` changes tool list/order | Tool schemas are often part of the very beginning of the cache key | Use a fixed, canonical, sorted tool set for the workflow; avoid unused tools if possible. |
| 2 | `user.name` and `user.email` in instructions | Creates a different leading prefix per user; leaks identifiers into repeated system text | Move authorized user details to the dynamic message after shared context. |
| 3 | `datetime.now().isoformat()` in system text | Changes on each call, often at microsecond precision | Put time near the end, or use a task-relevant stable date. |
| 4 | Unsorted `json.dumps(user.preferences)` | Semantically equal objects may serialize in different key orders | Use `json.dumps(..., sort_keys=True)`, and place user-specific preferences after stable material. |
| 5 | `BASE_INSTRUCTIONS` appears *last* | The stable information is preceded by changing user/time text | Move fixed instructions to the beginning. |
| 6 | Question precedes shared documents | Each changing question prevents a long document from acting as shared prefix | Put permission-safe shared docs before the question; keep question last. |
| 7 | User-specific model / reasoning configuration | Caches are scoped to models and often sensitive to reasoning/settings changes | Standardize the model and relevant generation settings by workflow. |

**Recommended order:** **canonical fixed tools → BASE_INSTRUCTIONS → shared, authorized documents → user attributes/preferences → coarse date → unique question**. A cache marker on a changing prefix does not solve these issues. A fixed tool list must still respect authorization: never pass tools the user is forbidden to invoke. The demonstration before/after implementation is in [`src/invalidators.py`](src/invalidators.py).

## Exercise 4 — Parallel vs. sequenced

**Workload:** 200 requests × 30,000 shared prefix tokens + 300 output tokens each. Total output tokens 60,000 = **$0.600** at $10/M, or **$0.300** at half-price batch rates.

| Pattern | Cached-prefix input cost | Output cost | Total |
|---|---:|---:|---:|
| 1. All 200 concurrent, each a fresh 1.25× write | 200 × $0.075 = **$15.000** | $0.600 | **$15.600** |
| 2. One warm-up write then 199 cached reads | $0.075 + 199 × $0.006 = **$1.269** | $0.600 | **$1.869** |
| 3. Same warm-up+199 structure, 50%-off batch on all components | **$0.6345** | $0.300 | **$0.9345** |
| 1 (no write premium): all 200 first writes at normal input rate | 200 × $0.060 = **$12.000** | $0.600 | **$12.600** |
| 2 (no write premium): one normal write then 199 reads | $0.060 + 199 × $0.006 = **$1.254** | $0.600 | **$1.854** |

Warm-up saves **88.0%** relative to all-parallel with premium, and warm-up plus assumed batch saves **94.0%**. Without a write premium, warm-up saves **85.3%**. This comparison assumes the 199 simultaneous requests can read a fully warmed cache entry. Batch discounts on cache reads **may not stack** for every provider; this lab explicitly instructs us to assume they do.

## Exercise 5 — Find batch candidates

These are **five illustrative engineering/team workflows**, not a claim about actual client projects or internal production traffic.

| Workload | Someone waiting now? | Large stable shared prefix? | Recommendation | Why |
|---|---|---|---|---|
| Nightly support ticket classification | No | Yes | **Both** | Asynchronous and repeated policy instructions. |
| Weekly retrospective summaries | No | Yes | **Both** | Scheduled runs with reusable summary guidelines. |
| Scheduled documentation consistency reviews | No | Yes | **Both** | Many similar checks against stable review policy. |
| Interactive developer code review | Yes | Yes | **Cache** | Latency matters, but shared review instructions can still be cached. |
| Immediate support chat replies | Yes | No | **Neither** | User-specific fast replies; neither batch latency nor repeated shared prefix assumed. |

**Best candidate:** nightly support ticket classification. **Assumptions** (hypothetical monthly estimate): 10,000 calls; 8,000 stable prompt tokens per call, 200 dynamic input, 250 output; one successful 8,000-token cache write for the month, 9,999 reads of that prefix, 50%-off batch discount applied to all token categories. Ignore TTL expiry, retries, and provider-specific stacking rules for the *idealized upper-bound* estimate.

| Cost component | Without optimization | Batch + cache (idealized) |
|---|---:|---:|
| Monthly total | **$189.0000** | **$22.5092** |
| Estimated monthly saving | | **$166.4908 (88.1%)** |

The estimate intentionally makes strong assumptions; real overnight batches spanning TTL boundaries may need multiple cache writes, and batch/cache pricing may not combine this way. Code for recomputing scenarios is in [`src/batch_candidates.py`](src/batch_candidates.py).

## Wrap-up — Back to the Lab 1 baseline

The earlier Lab 1 `plain_call` for the synthetic invoice question used **68 input tokens and 58 output tokens** in one Ollama `qwen2.5:3b` call, with no shared large document and no evidence of cached input. The stable portions are the small instructions and invoice-question template, but no cache-hit evidence exists and a one-turn task provides almost no repeated-prefix opportunity. If thousands of independent invoice requests were available and latency did not matter, they could be **batched**, but this single interactive call should remain a normal request.

**Previous evidence:** https://github.com/kNightRunner/taller-academy-fde-day1-foundations/blob/main/results/experiments.json (`plain_call`). The observed response avoided inventing the invoice due date but did not complete the numerical task. No new experimental outcome is claimed.

## Reproducibility / grading notes

**Arithmetic:** exercises 1 and 4 show full calculations and no-premium alternatives. **Cache behavior:** exercise 2 declares predictions before any usage and includes an honest paper model, including case D's below-minimum context. **Code review:** seven invalidators/fixes with a final ordering and runnable educational code. **Application:** five classified workloads and a numerical monthly estimate with assumptions. **No tests were run** at the author's request. See `docs/HOW_TO_MEASURE.md` for optional manual measurement instructions.
