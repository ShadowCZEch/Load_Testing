from datetime import datetime
import csv
import time
from pathlib import Path

# ================================================================
# CSV generation header
# ================================================================
REACHABILITY_HEADER  = ["timestamp", "status"]
STATE_CHANGE_HEADER  = ["timestamp", "direction"]
SUMMARY_HEADER       = ["session_start", "metric", "value"]

def _init_csv(path: Path, header: list[str]) -> None:
    if not path.exists():
        with path.open("w", newline="") as f:
            csv.writer(f).writerow(header)

def _overwrite_csv(path: Path, header: list[str]) -> None:
    with path.open("w", newline="") as f:
        csv.writer(f).writerow(header)

def _append_csv(path: Path, row: list) -> None:
    with path.open("a", newline="") as f:
        csv.writer(f).writerow(row)


def _write_session_separator(path: Path, session_start: str) -> None:
    with path.open("a", newline="") as f:
        w = csv.writer(f)
        w.writerow([])
        w.writerow([f"# session: {session_start}"])


def _write_summary(path: Path, session_start: str, stats: dict,
                   append: bool) -> None:
    with path.open("a", newline="") as f:
        w = csv.writer(f)
        if append:
            w.writerow([])
            w.writerow([f"# session: {session_start}"])
        for metric, value in stats.items():
            w.writerow([session_start, metric, value])

# ================================================================
# Reachability tools
# ================================================================
def one_ping(ipaddr, timeout, iface=None):
    try:
        import subprocess
        cmd = ["ping", "-c", "1", "-W", str(int(timeout))]
        if iface:
            cmd += ["-I", iface]
        cmd.append(ipaddr)
        result = subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return result.returncode == 0
    except Exception:
        return False

def Watchdog(ipaddr=None, poll_interval=None, duration=None,
             output_dir: str = "data", append: bool = True):

    if not poll_interval:
        raise ValueError("poll_interval must be provided.")

    if not ipaddr:
        raise ValueError("ipaddr must be provided.")

    poll_interval = float(poll_interval)
    ping_timeout  = min(0.8, poll_interval)
    timeout       = max(1.0, ping_timeout)


    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)

    reachability_csv = out / "reachability.csv"
    state_changes_csv = out / "state_changes.csv"
    summary_csv = out / "summary.csv"

    session_start = datetime.now().strftime("%d-%m-%Y %H:%M:%S")

    if append:
        # Preserve existing data; add session marker so runs are distinguishable
        _init_csv(reachability_csv, REACHABILITY_HEADER)
        _init_csv(state_changes_csv, STATE_CHANGE_HEADER)
        _init_csv(summary_csv, SUMMARY_HEADER)
        _write_session_separator(reachability_csv, session_start)
        _write_session_separator(state_changes_csv, session_start)
    else:
        # Fresh start: truncate all three files
        _overwrite_csv(reachability_csv, REACHABILITY_HEADER)
        _overwrite_csv(state_changes_csv, STATE_CHANGE_HEADER)
        _overwrite_csv(summary_csv, SUMMARY_HEADER)

    # counters
    total_changes = 0
    went_offline = 0
    came_online = 0
    last_state = None

    print(f"Running server monitoring on {ipaddr}, probing every {poll_interval}s.")

    try:
        while True:
            start_time = time.time()
            timestamp = datetime.now().strftime("%d-%m-%Y %H:%M:%S")
            up = one_ping(ipaddr,timeout)
            status = "up" if up else "down"

            _append_csv(reachability_csv, [timestamp, status])

            if last_state is None:
                last_state = up
                print(f"[{timestamp}]  {'Server is online' if up else 'Server is unavailable'}", flush=True)

            elif up != last_state:
                direction = "down -> up" if up else "up -> down"
                _append_csv(state_changes_csv, [timestamp, direction])
                total_changes += 1
                if up:
                    came_online += 1
                else:
                    went_offline += 1
                last_state = up
                print(f"[{timestamp}]  {'Server is back up running' if up else 'Server is unavailable'}", flush=True)

            elapsed = time.time() - start_time
            sleep_time = max(0.0, float(poll_interval - elapsed))
            time.sleep(sleep_time)
            if duration is not None and (time.time() - start_time) >= float(duration):
                print("\nMonitoring duration reached, stopping.")
                break
    except KeyboardInterrupt:
        print("\nMonitoring interrupted by user.")

