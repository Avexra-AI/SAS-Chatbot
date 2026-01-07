import json
from pathlib import Path

STATE_FILE = Path("state.json")

def load_state():
    if STATE_FILE.exists():
        return json.loads(STATE_FILE.read_text())
    return {
        "last_sync_date": "20260101",
        "processed_vouchers": []
    }

def save_state(state):
    STATE_FILE.write_text(json.dumps(state, indent=2))
