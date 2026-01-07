import time
from datetime import datetime
from tally_source import fetch_daybook
from xml_sanitizer import sanitize
from normalizer import normalize
from state import load_state, save_state
from store import upsert

POLL_INTERVAL = 60

def run():
    state = load_state()

    while True:
        try:
            today = datetime.now().strftime("%Y%m%d")

            raw = fetch_daybook(state["last_sync_date"], today)
            clean = sanitize(raw)
            vouchers = normalize(clean)

            for v in vouchers:
                if v["fingerprint"] in state["processed_vouchers"]:
                    continue

                upsert(v)
                state["processed_vouchers"].append(v["fingerprint"])

            state["last_sync_date"] = today
            save_state(state)

            print(f"[OK] synced {len(vouchers)} vouchers")

        except Exception as e:
            print("[ERROR]", e)

        time.sleep(POLL_INTERVAL)

if __name__ == "__main__":
    run()
