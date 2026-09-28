"""Part 2 — Operational movement flagging and state persistence."""
import json
from pathlib import Path
from datetime import datetime, timezone

STATE_FILE = Path(__file__).resolve().parent / "metrics_state.json"

def compute_percentage_change_v1(current, previous):
    if previous in (0, None):
        return 0.0
    return round((current - previous) / previous * 100, 2)

def flag_significant_regions_v1(changes, threshold=8):
    """Operational alert flag, not a statistical significance test."""
    return {
        region: change
        for region, change in changes.items()
        if change is not None and abs(change) > threshold
    }

def save_state(state, path=STATE_FILE):
    Path(path).write_text(json.dumps(state, indent=2), encoding="utf-8")

def load_state(path=STATE_FILE):
    return json.loads(Path(path).read_text(encoding="utf-8"))

def main():
    april_may = {
        "Bengaluru": -15.02, "Guntur": 122.19, "Hyderabad": 16.29,
        "Karimnagar": 23.63, "Nellore": 6.50, "Tirupati": 66.87,
        "Vijayawada": 2.06, "Visakhapatnam": -62.46, "Warangal": -22.03
    }
    may_june = {
        "Bengaluru": -1.52, "Guntur": -28.11, "Hyderabad": 20.61,
        "Karimnagar": -44.00, "Nellore": 3.52, "Tirupati": -17.07,
        "Vijayawada": -12.02, "Visakhapatnam": 99.12, "Warangal": -14.84
    }
    state = {
        "run_id": datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ"),
        "threshold": 8,
        "april_to_may_flags": flag_significant_regions_v1(april_may),
        "may_to_june_flags": flag_significant_regions_v1(may_june),
    }
    save_state(state)
    print(json.dumps(state, indent=2))

if __name__ == "__main__":
    main()
