"""Lab 3 pricing: illustrative USD per million tokens, not provider quotes."""
from dataclasses import dataclass

INPUT = 2.00
OUTPUT = 10.00
CACHED = 0.20
WRITE_PREMIUM = 2.50


@dataclass(frozen=True)
class Usage:
    uncached_input: int = 0
    cache_write: int = 0
    cached_input: int = 0
    output: int = 0

    def input_cost(self, write_rate=WRITE_PREMIUM):
        return (self.uncached_input * INPUT + self.cache_write * write_rate
                + self.cached_input * CACHED) / 1_000_000

    def cost(self, write_rate=WRITE_PREMIUM, batch=False):
        regular = self.input_cost(write_rate) + self.output * OUTPUT / 1_000_000
        return regular * (0.5 if batch else 1)

    def as_dict(self):
        return dict(uncached_input=self.uncached_input,
                    cache_write=self.cache_write,
                    cached_input=self.cached_input, output=self.output)


def total_cost(calls, write_rate=WRITE_PREMIUM, batch=False, input_only=False):
    factor = 0.5 if batch else 1.0
    return sum(c.input_cost(write_rate) if input_only else c.cost(write_rate)
               for c in calls) * factor if input_only else sum(c.cost(write_rate, batch) for c in calls)


def fixed_ttl_calls(minutes, ttl_minutes, document_tokens=20_000,
                    premiums=True):
    """Non-sliding TTL; expiry is measured from the last write, not from reads."""
    expiry = None
    out = []
    for minute in minutes:
        if expiry is None or minute >= expiry:
            out.append(Usage(cache_write=document_tokens) if premiums
                       else Usage(uncached_input=document_tokens))
            expiry = minute + ttl_minutes
        else:
            out.append(Usage(cached_input=document_tokens))
    return out


def refreshed_ttl_calls(minutes, ttl_minutes, document_tokens=20_000,
                        premiums=True):
    """Explicit sliding-TTL assumption used in the course's supplied check numbers."""
    last_access = None
    out = []
    for minute in minutes:
        if last_access is None or minute - last_access >= ttl_minutes:
            out.append(Usage(cache_write=document_tokens) if premiums
                       else Usage(uncached_input=document_tokens))
        else:
            out.append(Usage(cached_input=document_tokens))
        last_access = minute
    return out


def evaluation_usage(num_calls=200, prefix=30_000, output_each=300,
                     warmup=False, premium=True):
    writes = 1 if warmup else num_calls
    reads = num_calls - writes
    if premium:
        return [Usage(cache_write=prefix, output=output_each)] * writes + [
            Usage(cached_input=prefix, output=output_each)] * reads
    return [Usage(uncached_input=prefix, output=output_each)] * writes + [
        Usage(cached_input=prefix, output=output_each)] * reads
