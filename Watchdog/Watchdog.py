import sys
import subprocess
import time
from datetime import datetime
import ipaddress
from pathlib import Path

class Watchdog:
    def __init__(self):
        self.pick = None
        self.ipaddr = None
        self.interval = None
        self.cmd_base = None
        self.poll_interval = 1.0
        self.last_state = None
        self.last_report_time = 0.0

    @staticmethod
    def parse_ping_success(out_bytes):
        out = out_bytes.decode("utf-8", errors="ignore").lower()
        if ("1 received" in out) or ("bytes from" in out) or ("bytes=" in out and "ttl=" in out):
            return True
        return False

    def load_config_file(self, path="watchdog.conf"):
        pathp = Path(path)
        if not pathp.is_file():
            raise FileNotFoundError(f"Konfigurační soubor nenalezen: {path}")
        cfg = {}
        with pathp.open("r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                if "=" not in line:
                    continue
                k, v = line.split("=", 1)
                cfg[k.strip().lower()] = v.strip()

        pick = cfg.get("pick")
        if pick is None:
            raise ValueError("Chybná nebo chybějící volba 'pick' (4 nebo 6).")
        pick = str(pick).strip()
        if pick not in ("4", "6"):
            raise ValueError("Chybná hodnota 'pick', očekává se 4 nebo 6.")

        ipaddr = cfg.get("ipaddr")
        if not ipaddr:
            raise ValueError("Chybi 'ipaddr' v konfiguračním souboru.")
        ipaddr = ipaddr.strip()
        try:
            if pick == "4":
                ipaddress.IPv4Address(ipaddr)
            else:
                ipaddress.IPv6Address(ipaddr)
        except ValueError:
            raise ValueError("Špatně zadaná IP adresa pro zvolený režim.")

        interval = cfg.get("interval")
        if interval is None:
            raise ValueError("Chybí 'interval' v konfiguračním souboru.")
        interval = interval.strip()
        try:
            interval_val = int(interval)
        except ValueError:
            raise ValueError("Interval musí být celé číslo.")
        if interval_val <= 0:
            raise ValueError("Interval musí být kladné celé číslo.")

        poll = cfg.get("poll_interval")
        if poll is not None:
            try:
                self.poll_interval = float(poll.strip())
            except Exception:
                self.poll_interval = 1.0

        self.pick = pick
        self.ipaddr = ipaddr
        self.interval = interval_val

    def CmdSelect(self):
        try:
            pick_val = str(self.pick).strip()
        except Exception:
            pick_val = None

        if pick_val == "4":
            if sys.platform == "win32":
                self.cmd_base = ["ping", "-n", "1", self.ipaddr]
            else:
                self.cmd_base = ["ping", "-c", "1", "-W", "1", self.ipaddr]
            return

        if pick_val == "6":
            if sys.platform == "win32":
                self.cmd_base = ["ping", "-6", "-n", "1", self.ipaddr]
            else:
                self.cmd_base = ["ping", "-6", "-c", "1", "-W", "1", self.ipaddr]
            return

        print("ERROR: Neznámý pick v CmdSelect. Stav:", repr(self.pick))
        raise RuntimeError("Neznámý pick při sestavování příkazu ping.")

    def one_ping(self):
        cmd = self.cmd_base
        timeout = min(0.8, float(self.poll_interval))
        try:
            r = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=timeout)
            success = self.parse_ping_success(r.stdout)
            return success, r.stdout, r.stderr
        except subprocess.TimeoutExpired as e:
            return False, getattr(e, "stdout", b""), getattr(e, "stderr", b"")

    def PingSetup(self):
        print(f"Spouštím monitoring serveru {self.ipaddr} každých {self.interval} sekund. Ukonči pomocí Ctrl+C.\n")
        ping_timeout = min(0.8, self.poll_interval)
        timeout_val = max(1.0, ping_timeout)
        for _ in range(2):
            try:
                subprocess.run(self.cmd_base, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=timeout_val)
            except subprocess.TimeoutExpired:
                pass
        self.last_report_time = 0.0

    def StatusLoop(self):
        last_state = self.last_state
        try:
            while True:
                start_time = time.time()
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                up, out, err = self.one_ping()

                if last_state is None:
                    last_state = up
                    self.last_report_time = start_time
                    print(f"[{timestamp}]  {'Server běží' if up else 'Server spadl nebo je nedostupný'}", flush=True)
                else:
                    if up != last_state:
                        last_state = up
                        self.last_report_time = start_time
                        print(f"[{timestamp}]  {'Server se vrátil online' if up else 'Server je nedostupný'}", flush=True)
                    else:
                        if start_time - self.last_report_time >= self.interval:
                            self.last_report_time = start_time
                            print(f"[{timestamp}]  {'Server stále běží' if up else 'Server stále nedostupný'}", flush=True)
                elapsed = time.time() - start_time
                sleep_time = max(0.0, self.poll_interval - elapsed)
                time.sleep(sleep_time)
        except KeyboardInterrupt:
            print("\nMonitoring ukončen uživatelem.")

# --- config resolution helpers (ke spuštění v run) ---

def find_config_in_script_dir(filename="watchdog.conf"):
    try:
        script_dir = Path(__file__).resolve().parent
    except NameError:
        script_dir = Path.cwd()
    candidate = script_dir / filename
    if candidate.is_file():
        return str(candidate.resolve())
    return None

def ask_user_for_config(filename="watchdog.conf"):
    try:
        user_input = input(f"Konfig {filename} nebyl nalezen v adresáři se skripty. Zadej cestu ke konfigu ve formátu cesta/soubor.conf nebo stiskni Enter pro ukončení: ").strip()
    except EOFError:
        user_input = ""
    if not user_input:
        return None
    user_path = Path(user_input).expanduser()
    if user_path.is_file():
        return str(user_path.resolve())
    return None

def resolve_config_path(preferred_arg=None, filename="watchdog.conf"):
    if preferred_arg:
        p = Path(preferred_arg).expanduser()
        if p.is_file():
            return str(p.resolve())
    cfg = find_config_in_script_dir(filename)
    if cfg:
        return cfg
    alt = Path("/hgfs/Work") / filename
    if alt.is_file():
        return str(alt.resolve())
    return ask_user_for_config(filename)

# --- jediná run funkce která udělá vše pro jednu instanci ---
def run():
    # přečti CLI argument uvnitř modulu, main.py už nic nemusí řešit
    cfg_arg = sys.argv[1] if len(sys.argv) > 1 else None

    cfg_path = resolve_config_path(cfg_arg, "watchdog.conf")
    if not cfg_path:
        print("Konfig nebyl zadán nebo nalezen. Ukončuji.")
        raise SystemExit(1)

    w = Watchdog()
    try:
        w.load_config_file(cfg_path)
    except Exception as e:
        print("Chyba při načítání konfigurace:", e)
        raise SystemExit(1)

    # debug kontrola stavu naplněné instance
    print("Načtené uživatelské hodnoty:")
    print("Protokol:",repr(w.pick))
    print("IP Adresa:", repr(w.ipaddr))
    print("Interval výpisů:", repr(w.interval),"sekund")
    w.CmdSelect()
    w.PingSetup()
    w.StatusLoop()