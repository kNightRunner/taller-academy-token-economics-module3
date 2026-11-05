"""Optional real-provider experiment; never required for paper submission.

Uses OpenAI Responses API when OPENAI_API_KEY and OPENAI_MODEL are configured.
No provider calls occur during import. This module does not fake reported hits.
"""
import os
from dataclasses import dataclass
from .pricing import Usage


@dataclass
class Result:
    text: str
    usage: Usage
    model: str


class OpenAIAdapter:
    def __init__(self, model=None):
        from openai import OpenAI
        self.client = OpenAI()
        self.model = model or os.environ["OPENAI_MODEL"]

    def ask(self, instructions, question, max_output_tokens=160):
        response = self.client.responses.create(
            model=self.model,
            instructions=instructions,
            input=question,
            max_output_tokens=max_output_tokens,
        )
        u = response.usage
        cached = getattr(getattr(u, "input_tokens_details", None),
                         "cached_tokens", 0) or 0
        usage = Usage(uncached_input=u.input_tokens - cached,
                      cached_input=cached, cache_write=0,
                      output=u.output_tokens)
        return Result(response.output_text, usage, self.model)
