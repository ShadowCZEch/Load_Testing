# locustfile.py

from gevent import monkey

monkey.patch_all()

from Config_Load import Config_Load
from Packet_create import tcp_packet, udp_packet
from Port_scanner import scan_ports_tcp, scan_ports_udp
from pathlib import Path
import sys
import os
import subprocess
import time
from locust import User, task, events, constant
from gevent import sleep

cfg = None

def cfg_int(key):
    if cfg is None:
        return None
    k = cfg.get(key)
    if k is None:
        return None
    try:
        return int(k)
    except (TypeError, ValueError):
        raise ValueError(f"Invalid number format in config file")

def cfg_str(key):
    if cfg is None:
        return None
    k = cfg.get(key)
    if k is None:
        return None
    try:
        return str(k)
    except (TypeError, ValueError):
        raise ValueError(f"Invalid format in config file")

LOCUST_MODE = os.environ.get("LOCUST_MODE")

class UserClass(User):

    wait_time = constant(0)  # default, přepíšeme níže

    @task
    def keep_send(self):

        if LOCUST_MODE == "tcp":
            for _ in range(100):
                start = time.perf_counter()
                tcp_packet()
                rt = (time.perf_counter() - start) * 1000
                self.environment.events.request.fire(
                    request_type="TCP",
                    name="tcp_flood",
                    response_time=rt,
                    response_length=0,
                    exception=None,
                )
                sleep(0)


        if LOCUST_MODE == "udp":
            for _ in range(100):
                start = time.perf_counter()
                udp_packet()
                rt = (time.perf_counter() - start) * 1000
                self.environment.events.request.fire(
                    request_type="UDP",
                    name="udp_flood",
                    response_time=rt,
                    response_length=0,
                    exception=None,
                )
                sleep(0)

        else:
            UserClass.wait_time = constant(0)


def on_test_start(environment):
    user_count = environment.runner.user_classes.count(UserClass) if "UserClass" in globals() else 0

    events.request.fire(
        request_type="INFO",
        name="tcp_users_count",
        response_time=0,
        response_length=user_count,
        exception=None,
    )
    sleep(0)

def run_locust_headless_and_make_report(locustfile: str = "locustfile.py",
                                        users: int = cfg_int("unique_users_count"),
                                        spawn_rate: int = cfg_int("spawn_rate"),
                                        run_time: str = cfg_str("time_total"),
                                        html_out: str = "report.html"):

    locust_path = Path(locustfile).resolve()
    html_out_p = Path(html_out).resolve()

    if users is None:
        raise ValueError("Users parameter not correctly loaded.")
    if run_time is None:
        raise ValueError("Runtime parameter not correctly loaded.")
    if spawn_rate is None:
        raise ValueError("Spawn rate parameter not correctly loaded.")
    cmd = [sys.executable, "-m", "locust", "-f", str(locust_path), "--headless",
           "-u", str(users), "-r", str(spawn_rate), "--run-time", run_time, "--html", str(html_out_p)]
    env = os.environ.copy()
    env["LOCUST_MODE"] = protocol
    return cmd,env

if __name__ == "__main__" and not os.environ.get("LOCUST_MODE"):

    cfg = Config_Load()

    host_ip = cfg.get("ipaddr")

    protocol = cfg.get("protocol", "").lower()


    if protocol == "tcp":
        print("Chosen mode: TCP Flood")
        print("Starting TCP scan")
        scanner = scan_ports_tcp

    elif protocol == "udp":
        print("Chosen mode: UDP Flood")
        print("Starting UDP scan")
        scanner = scan_ports_udp

    else:
        raise ValueError("Invalid protocol")

    try:
        users = cfg_int("unique_users_count")
        spawn_rate = cfg_int("spawn_rate")
        run_time = cfg_str("time_total")
        html_out = "report.html"
    except Exception as e:
        print("Error when loading configuration from file:",e,file=sys.stderr)
        sys.exit(2)

    port = scanner()
    host = f"{host_ip}:{port}"

    try:
        cmd,env = run_locust_headless_and_make_report(
            locustfile=__file__,
            users=users,
            spawn_rate=spawn_rate,
            run_time=run_time,
            html_out=html_out,
        )

        cmd += ["--host", host]

        print("Running Locust:", " ".join(cmd))
        subprocess.check_call(cmd)
    except subprocess.CalledProcessError as e:
        print("Error when running Locust process:",e,file=sys.stderr)
        sys.exit(3)
    except Exception as e:
        print("Error generating report:",e,file=sys.stderr)
        sys.exit(4)