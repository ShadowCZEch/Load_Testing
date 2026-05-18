# Locust_tcp.py

import os
from Packet_create import tcp_packet
import time
import random
from locust import User, task, constant, constant_throughput
from gevent import sleep

TARGET_HOST = os.environ.get("TARGET_HOST", "")
TARGET_PORT = int(os.environ.get("TARGET_PORT", 0))
TARGET_RPS = float(os.environ.get("TARGET_RPS", 0))
print(f"[Locust] TARGET_RPS = {TARGET_RPS}")

_ip_pool = []

def _load_pool():
    global _ip_pool
    if _ip_pool:
        return
    pool_file = os.environ.get("IP_POOL_FILE")
    print(f"[Locust] IP_POOL_FILE = {pool_file}")
    if pool_file and os.path.exists(pool_file):
        with open(pool_file, "r") as f:
            _ip_pool = [line.strip() for line in f if line.strip()]
        print(f"[Locust] Loaded {len(_ip_pool)} source IPs.")
    else:
        print(f"[ERROR] Pool file not found: {pool_file}")

class UserClass(User):
    source_ip = None
    if TARGET_RPS > 0:
        wait_time = constant_throughput(TARGET_RPS)
    else:
        wait_time = constant(0)

    def on_start(self):
        _load_pool()
        if not _ip_pool:
            raise Exception("IP pool is empty — check IP_POOL_FILE")
        self.source_ip = random.choice(_ip_pool)

    @task
    def keep_send(self):

        start = time.perf_counter()
        try:
            tcp_packet(dst_port=TARGET_PORT, src_ip=self.source_ip)
            rt = (time.perf_counter() - start) * 1000

            self.environment.events.request.fire(
                request_type="TCP",
                name="tcp_flood",
                response_time=rt,
                response_length=0,
                exception=None,
            )
        except Exception as e:
            self.environment.events.request.fire(
                request_type="TCP",
                name="tcp_flood",
                response_time=0,
                response_length=0,
                exception=e,
            )
        sleep(0)

