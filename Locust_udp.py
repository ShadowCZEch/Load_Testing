# locustfile_udp.py

import os
from gevent import monkey
import time
import queue
from locust import User, task, events, constant
from gevent import sleep

monkey.patch_all()

TARGET_PORT = int(os.environ.get("TARGET_PORT", 0))

ip_queue = queue.Queue()

@events.test_start.add_listener
def on_test_start( **_kwargs):
    pool_file = os.environ.get("IP_POOL_FILE")
    if pool_file and os.path.exists(pool_file):
        with open(pool_file, "r") as f:
            for line in f:
                addr = line.strip()
                if addr:
                    ip_queue.put(addr)
        print(f"[Locust] Načteno {ip_queue.qsize()} unikátních zdrojových IP.")
    else:
        print("[Error] Soubor s IP pool nebyl nalezen!")

class UserClass(User):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.source_ip = None

    wait_time = constant(0)

    def on_start(self):
        try:
            self.source_ip = ip_queue.get_nowait()
        except queue.Empty:
            self.source_ip = None

    @task
    def keep_send(self):
        from Packet_create import  udp_packet

        start = time.perf_counter()
        try:
            udp_packet(dst_port=TARGET_PORT, src_ip=self.source_ip)
            rt = (time.perf_counter() - start) * 1000
            self.environment.events.request.fire(
                request_type="UDP",
                name="udp_flood",
                response_time=rt,
                response_length=0,
                exception=None,
                )
        except Exception as e:
            self.environment.events.request.fire(
                request_type="UDP",
                name="udp_flood",
                response_time=0,
                response_length=0,
                exception=e,
                )
        sleep(0)

