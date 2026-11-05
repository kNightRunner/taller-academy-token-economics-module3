"""Four manual, opt-in caching experiment configurations.

Run from repository root: python -m src.experiments --provider openai
Requires configured API credentials and a sufficiently long doc.txt.
"""
import argparse
import json
import time
from datetime import datetime, timezone
from pathlib import Path
from .provider import OpenAIAdapter
from .pricing import total_cost

QUESTIONS = (
    "Summarize the document in one sentence.",
    "List three key terms it uses.",
    "What is the single most important rule in it?",
)


def run_experiment(adapter, doc, experiment, pause=2):
    rows = []
    for index, question in enumerate(QUESTIONS, start=1):
        timestamp = datetime.now(timezone.utc).isoformat()
        if experiment == "A":
            instructions, user_question = doc, question
        elif experiment == "B":
            instructions = f"Current time: {timestamp}\n\n" + doc
            user_question = question
        elif experiment == "C":
            instructions, user_question = doc, f"{question}\n\nCurrent time: {timestamp}"
        elif experiment == "D":
            instructions, user_question = " ".join(doc.split()[:300]), question
        else:
            raise ValueError("Choose A, B, C, or D")
        result = adapter.ask(instructions, user_question)
        record = {"experiment": experiment, "call": index,
                  "model": result.model, "normalized_usage": result.usage.as_dict(),
                  "input_cost_usd_course_rate": result.usage.input_cost(write_rate=2.0),
                  "output": result.text}
        rows.append(record)
        if index < len(QUESTIONS):
            time.sleep(pause)
    return rows


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--provider", choices=["openai"], required=True)
    parser.add_argument("--doc", default="doc.txt")
    parser.add_argument("--output", default="results/observed_experiment_2.json")
    parser.add_argument("--pause", type=float, default=2)
    args = parser.parse_args()
    doc = Path(args.doc).read_text(encoding="utf-8")
    if len(doc.split()) < 5000:
        raise SystemExit("Use a larger document; verify >=5000 tokens with tokenizer before paying for requests.")
    adapter = OpenAIAdapter()
    records = []
    for label in "ABCD":
        records.extend(run_experiment(adapter, doc, label, pause=args.pause))
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps({"provider": "openai", "mode": "observed",
                                      "note": "OpenAI reports no cache write counter",
                                      "calls": records}, indent=2), encoding="utf-8")
    print(f"Recorded {len(records)} observed calls to {output_path}")


if __name__ == "__main__":
    main()
