# Optional validation — user-run only

No tests, SDK requests, or command executions are part of the initial Lab 3 submission.

## Exercise 2: Real API (optional)

1. Select a model/provider with prompt caching, check its *current* minimum prefix size and any cache TTL.
2. Prepare a synthetic `doc.txt` of at least 5,000 tokens, not just 5,000 words. Do not include customer information.
3. Set `OPENAI_API_KEY` and `OPENAI_MODEL` locally. Do not commit `.env` or the document.
4. Install `requirements.txt`; run `python -m src.experiments --provider openai --doc doc.txt` locally.
5. Review `results/observed_experiment_2.json`. Compare with `docs/EXPERIMENT_2_PAPER.md` and note mismatches.
6. If A produces zero cached tokens, retry A before drawing a conclusion. Real responses reflect model-specific caching and may be best-effort.
7. If you submit real measurements, update `SUBMISSION.md` manually and distinguish them from the paper estimates.

The supplied runner uses OpenAI's Responses API. Cached-token usage is normalized to `cached_input`; noncached input is `total_input - cached_input`. OpenAI does not provide a separate cache-write-premium counter. The exercise's premium-paper model is distinct from OpenAI billing behavior. `max_output_tokens` limits output but is not itself a cache parameter.

## Exercises 1 and 4

Read `src/pricing.py` to adapt assumptions if your provider has absolute TTL expiration rather than a sliding TTL. The course's 15-minute check figures rely on refresh-on-access or another effective retention arrangement; don't assume all real caches behave that way.

## Exercise 5

Replace illustrative examples with your team's own non-sensitive, documented workload metrics (calls, prefix size, output size, latency tolerance). Consider rate limits, provider-specific batch eligibility, read/write TTL, and whether cache and batch discounts can stack.

## Security

Keep API tokens in the environment; use a synthetic `doc.txt`; review the provider's data-retention policy before uploading real documents; avoid printing or committing secrets. Nothing is automatically scheduled or invoked.
