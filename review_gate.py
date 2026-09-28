"""Part 3 — Human review gate with test harness and JSONL audit log."""
import json
from datetime import datetime, timezone
from pathlib import Path
import uuid

BASE = Path(__file__).resolve().parent
AUDIT = BASE / "audit_log.jsonl"

VALID = {"approve", "edit", "reject"}

def review_gate_v1(report, decision, reviewer_note="", region="Guntur", run_id=None):
    if decision not in VALID:
        raise ValueError(f"Invalid decision: {decision}. Use approve/edit/reject.")
    entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "run_id": run_id or str(uuid.uuid4()),
        "region": region,
        "decision": decision,
        "reviewer_note": reviewer_note,
    }
    with AUDIT.open("a", encoding="utf-8") as f:
        f.write(json.dumps(entry) + "\n")
    return decision == "approve", entry

def test_harness():
    report = "Draft CII report for review."
    for decision in ["approve", "edit", "reject"]:
        allowed, entry = review_gate_v1(report, decision, f"Test {decision}")
        print(decision, "downstream_allowed=", allowed)
    try:
        review_gate_v1(report, "invalid")
    except ValueError:
        print("invalid decision correctly rejected")
    print("Audit log:", AUDIT)

if __name__ == "__main__":
    test_harness()
