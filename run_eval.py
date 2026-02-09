# eval/run_eval.py
"""
Offline evaluation runner (no Opik, no external imports from study_agent)
- Loads personas from eval/datasets/study_personas.json
- Calls Gemini 2.5 Flash-Lite to generate a plan JSON (using config=GenerateContentConfig)
- Computes heuristic metrics
- Prints PASS/FAIL per persona and a summary

Prereqs:
  pip install -r requirements.txt
  cp .env.example .env  # add GOOGLE_API_KEY=...
Run:
  python eval/run_eval.py
"""

import os
import json
from pathlib import Path
from dotenv import load_dotenv

# Official Google GenAI Python client
from google import genai
from google.genai import types as genai_types  # <-- added

# ------------------- Inlined instruction & metric logic -------------------

STUDY_SYSTEM_INSTRUCTION = """
You are a Study Planner agent. Create a realistic, sustainable plan.

Constraints:
- Respect daily_time_minutes and 'unavailable' dates.
- Smooth weekly load; no day > 40% of weekly hours.
- Include spaced revision: start around 20% weekly, increase near exam.
- Add a final consolidation/buffer window before exam.
- Prefer 45–90 minute sessions with 5–10 minute breaks.

Return JSON (application/json) with schema:
{
  "weekly_summary": [{ "week_start": "YYYY-MM-DD", "hours_planned": number, "focus": string }],
  "days": [{
    "date": "YYYY-MM-DD",
    "sessions": [
      { "subject": string, "topic": string, "minutes": number, "type": "learn|practice|revise" }
    ]
  }],
  "notes": string
}
"""

def _parse_plan_minutes(plan: dict) -> list[dict]:
    days = []
    for d in plan.get("days", []):
        minutes = sum(s.get("minutes", 0) for s in d.get("sessions", []))
        revise = sum(
            s.get("minutes", 0) for s in d.get("sessions", [])
            if s.get("type") == "revise"
        )
        days.append({"date": d.get("date"), "minutes": minutes, "revise_minutes": revise})
    return days

def compute_study_metrics(plan_json: dict, daily_time_minutes: int) -> dict:
    days = _parse_plan_minutes(plan_json)
    total = sum(d["minutes"] for d in days) or 1
    revise_total = sum(d["revise_minutes"] for d in days)

    overload_days = sum(1 for d in days if d["minutes"] > daily_time_minutes)

    avg = total / len(days) if days else 0
    variance = (
        sum((d["minutes"] - avg) ** 2 for d in days) / len(days) if days else 0
    )
    revision_ratio = revise_total / total

    final_two = days[-2:] if len(days) >= 2 else days
    final_buffer = int(all(d["minutes"] <= 0.6 * daily_time_minutes for d in final_two))

    return {
        "overload_days": overload_days,
        "weekly_load_variance": round(variance, 2),
        "revision_ratio": round(revision_ratio, 3),
        "final_buffer": final_buffer,
    }

# ------------------- Runner -------------------

MODEL = "gemini-2.5-flash-lite"   # fast & cost-efficient; 1M-token context
DATASET_RELATIVE = Path(__file__).parent / "datasets" / "study_personas.json"

def load_dataset() -> list[dict]:
    ds_path = DATASET_RELATIVE.resolve()
    print(f"[eval] Dataset path: {ds_path}")
    if not ds_path.exists():
        raise FileNotFoundError(
            f"Dataset not found at: {ds_path}\n"
            f"Create it or copy the seed JSON."
        )
    text = ds_path.read_text(encoding="utf-8")
    return json.loads(text)

def generate_plan_json(client: genai.Client, persona_input: dict) -> dict:
    payload = {
        **persona_input,
        "policy": {
            "max_daily_fraction_of_week": 0.4,
            "revision_baseline": 0.20,
        },
    }

    resp = client.models.generate_content(
        model=MODEL,
        contents=[
            {"role": "user", "parts": [{"text": STUDY_SYSTEM_INSTRUCTION}]},
            {"role": "user", "parts": [{"text": json.dumps(payload)}]},
        ],
        # ✅ Correct way in the current GenAI Python SDK:
        config=genai_types.GenerateContentConfig(
            temperature=0.6,
            response_mime_type="application/json",
        ),
    )

    raw = resp.text
    try:
        return json.loads(raw)
    except Exception as e:
        raise ValueError(
            "Model did not return valid JSON.\n"
            f"First 400 chars:\n{raw[:400]}"
        ) from e

def main():
    load_dotenv()
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise RuntimeError(
            "GOOGLE_API_KEY not set. Put it in .env (see .env.example)."
        )

    client = genai.Client(api_key=api_key)

    items = load_dataset()
    print(f"[eval] Loaded {len(items)} personas\n")

    passes = 0
    total = len(items)

    for idx, item in enumerate(items, 1):
        meta = item.get("metadata", {})
        label = meta.get("persona", f"case_{idx}")
        persona_input = item["input"]

        plan = generate_plan_json(client, persona_input)
        metrics = compute_study_metrics(plan, persona_input["daily_time_minutes"])

        overload_ok = metrics["overload_days"] <= item["expected"]["max_overload_days"]
        revision_ok = metrics["revision_ratio"] >= item["expected"]["min_revision_ratio"]
        ok = overload_ok and revision_ok
        if ok:
            passes += 1

        rev_pct = round(metrics["revision_ratio"] * 100)
        print(
            f"[{idx}/{total}] {label:12} | "
            f"overload_days={metrics['overload_days']}  "
            f"revision_ratio={rev_pct}%  "
            f"weekly_load_variance={metrics['weekly_load_variance']}  "
            f"{'PASS' if ok else 'FAIL'}"
        )

    print(f"\nSummary: {passes}/{total} passed")

if __name__ == "__main__":
    main()