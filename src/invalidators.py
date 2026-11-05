"""Educational version of the problematic request builder and its revision."""
import json
from datetime import datetime, timezone

BASE_INSTRUCTIONS = "Use verified facts, respect permissions, and be concise."
TOOLS = {
    "lookup_order": {"name": "lookup_order", "description": "Fetch synthetic order metadata"},
    "count_business_days": {"name": "count_business_days", "description": "Compute calendar-safe business days"},
}


def original_request(user, question, docs):
    tools = [TOOLS[name] for name in user.enabled_tools]
    instructions = (
        f"You are a helpful assistant for {user.name} ({user.email}).\n"
        f"Today is {datetime.now().isoformat()}.\n"
        f"User preferences: {json.dumps(user.preferences)}\n\n"
        + BASE_INSTRUCTIONS
    )
    return {"model": user.preferred_model,
            "reasoning": user.reasoning_setting,
            "tools": tools,
            "instructions": instructions,
            "input": f"Question: {question}\n\nReference documents:\n{docs}"}


def optimized_request(user, question, shared_docs, *, model, reasoning):
    """Stable ordering; shared docs must be authorized for this user's access.

    Stable instructions precede dynamic user details. Tools are kept in the
    same order for this workflow and are only included if the workflow uses them.
    """
    stable_tools = [TOOLS[name] for name in sorted(TOOLS)]
    stable_instructions = BASE_INSTRUCTIONS + "\n\nShared reference material:\n" + shared_docs
    dynamic_content = (
        f"User: {user.name}\nEmail: {user.email}\n"
        f"Preferences: {json.dumps(user.preferences, sort_keys=True)}\n"
        f"Date: {datetime.now(timezone.utc).date().isoformat()}\n"
        f"Question: {question}"
    )
    return {"model": model, "reasoning": reasoning,
            "tools": stable_tools, "instructions": stable_instructions,
            "input": dynamic_content}
