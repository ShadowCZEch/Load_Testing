# locustfile_tcp.py

import os
from Packet_create import tcp_packet
import time
import random
from locust import User, task, events, constant
from gevent import sleep


TARGET_PORT = int(os.environ.get("TARGET_PORT", 0))

_ip_pool = []


@events.test_start.add_listener
def on_test_start(**_kwargs):
    global _ip_pool
    pool_file = os.environ.get("IP_POOL_FILE")
    if pool_file and os.path.exists(pool_file):
        with open(pool_file, "r") as f:
            _ip_pool = [line.strip() for line in f if line.strip()]
            print(f"[Locust] Loaded {len(_ip_pool)} source IPs.")

    else:
        print("[Error] Soubor s IP pool nebyl nalezen!")

class UserClass(User):

    wait_time = constant(0)

    def on_start(self):
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

