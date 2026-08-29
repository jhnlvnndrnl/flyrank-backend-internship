"""
BE-07 Eval Runner — runs all test cases through the endpoint and prints the score.

Usage:
  1. Start the server:  uvicorn app.main:app --port 8000
  2. Run the eval:      python -m evals.run_eval

Each case is sent as a POST /enrich request. The script compares the returned
category against the expected category and prints the score.

On OpenRouter free tier, this uses 8 of your 50 daily calls. Budget for two runs.
"""

import json
import sys
import httpx
from pathlib import Path
from datetime import datetime, timezone


BASE_URL = "http://localhost:8000"
CASES_PATH = Path(__file__).resolve().parent / "cases.json"


def run_eval():
    """Run all eval cases and print results."""

    with open(CASES_PATH, "r", encoding="utf-8") as f:
        cases = json.load(f)

    print(f"\n{'='*60}")
    print(f"  BE-07 Eval Run — {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}")
    print(f"  Cases: {len(cases)}")
    print(f"{'='*60}\n")

    correct = 0
    total = len(cases)
    failures = []

    with httpx.Client(timeout=60.0) as client:
        for case in cases:
            case_id = case["id"]
            description = case["description"]
            expected_category = case["expected"]["category"]

            try:
                response = client.post(
                    f"{BASE_URL}/enrich",
                    json=case["input"],
                )

                if response.status_code == 200:
                    result = response.json()
                    actual_category = result.get("category", "MISSING")

                    if actual_category == expected_category:
                        correct += 1
                        status_icon = "✓"
                    else:
                        status_icon = "✗"
                        failures.append({
                            "id": case_id,
                            "description": description,
                            "expected": expected_category,
                            "actual": actual_category,
                            "reason": result.get("reason", "N/A"),
                        })
                else:
                    status_icon = "✗"
                    failures.append({
                        "id": case_id,
                        "description": description,
                        "expected": expected_category,
                        "actual": f"HTTP {response.status_code}",
                        "reason": response.text[:200],
                    })

                print(f"  {status_icon}  Case {case_id}: {description}")
                print(f"     Expected: {expected_category} | Got: {actual_category if response.status_code == 200 else f'HTTP {response.status_code}'}")
                if response.status_code == 200:
                    result = response.json()
                    print(f"     Confidence: {result.get('confidence', 'N/A')} | Reason: {result.get('reason', 'N/A')}")
                print()

            except httpx.ConnectError:
                print(f"  ✗  Case {case_id}: CONNECTION FAILED — is the server running on {BASE_URL}?")
                print(f"     Start it with: uvicorn app.main:app --port 8000")
                sys.exit(1)
            except Exception as e:
                print(f"  ✗  Case {case_id}: ERROR — {e}")
                failures.append({
                    "id": case_id,
                    "description": description,
                    "expected": expected_category,
                    "actual": f"ERROR: {e}",
                    "reason": str(e),
                })

    # --- Print summary ---
    score = correct / total if total > 0 else 0
    print(f"\n{'='*60}")
    print(f"  RESULT: {correct}/{total} ({score:.0%})")
    print(f"{'='*60}")

    if failures:
        print(f"\n  Failed cases:")
        for f in failures:
            print(f"    Case {f['id']}: {f['description']}")
            print(f"      Expected: {f['expected']} → Got: {f['actual']}")
            print(f"      Reason: {f['reason']}")
            print()

    print(f"\n  Date: {datetime.now(timezone.utc).strftime('%Y-%m-%d')}")
    print(f"  Prompt version: v1")
    print()

    return correct, total


if __name__ == "__main__":
    run_eval()
