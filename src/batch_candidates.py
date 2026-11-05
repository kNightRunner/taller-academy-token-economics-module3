"""Transparent estimates for sample team workflows; not real client usage."""
from dataclasses import dataclass
from .pricing import Usage

@dataclass(frozen=True)
class Workload:
    label: str
    immediate: bool
    shared_stable_prefix: bool
    recommendation: str

WORKLOADS = (
    Workload("Nightly ticket triage and classification", False, True, "both"),
    Workload("Weekly retrospective summaries", False, True, "both"),
    Workload("Scheduled documentation consistency reviews", False, True, "both"),
    Workload("Interactive developer code review", True, True, "cache"),
    Workload("Immediate support chat reply", True, False, "neither"),
)


def estimate_monthly_savings(calls=10_000, prefix_tokens=8_000,
                             dynamic_input_tokens=200, output_tokens=250):
    """Assume 1 cache write/month, all remaining requests hit and batch gets 50% off.

    Idealized scenario, not a guarantee of provider behavior.
    """
    baseline_per_call = Usage(uncached_input=prefix_tokens+dynamic_input_tokens,
                              output=output_tokens).cost()
    baseline = calls*baseline_per_call
    warmup = Usage(cache_write=prefix_tokens,
                   uncached_input=dynamic_input_tokens,
                   output=output_tokens)
    hit = Usage(cached_input=prefix_tokens,
                uncached_input=dynamic_input_tokens,
                output=output_tokens)
    batch_and_cache = warmup.cost(batch=True)+(calls-1)*hit.cost(batch=True)
    return {"calls_per_month":calls, "prefix_tokens":prefix_tokens,
            "dynamic_input_tokens":dynamic_input_tokens,
            "output_tokens":output_tokens, "baseline_usd":baseline,
            "optimized_usd":batch_and_cache,
            "savings_usd":baseline-batch_and_cache,
            "important_caveat": "One long-lived shared cache entry and batch/cache stacking assumed."}
