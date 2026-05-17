# Locust_tcp.py

import os
from Packet_create import tcp_packet
import time
import random
from locust import User, task, constant, events
from gevent import sleep
from scapy.all import AsyncSniffer
from typing import Optional

TARGET_HOST = os.environ.get("TARGET_HOST", "")
TARGET_PORT = int(os.environ.get("TARGET_PORT", 0))
SYNACK_TIMEOUT = float(os.environ.get("SYNACK_TIMEOUT", 5))

_ip_pool = []
_last_synack = None
_sniffer: Optional[AsyncSniffer] = None

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

def _on_synack(_):
    global _last_synack
    _last_synack = time.time()

def _start_sniffer():
    global _sniffer, _last_synack
    if _sniffer is not None:
        return
    _last_synack = None
    iface = os.environ.get("IFACE")
    _sniffer = AsyncSniffer(
        filter=f"src host {TARGET_HOST} and tcp and tcp[tcpflags] & (tcp-syn|tcp-ack) == (tcp-syn|tcp-ack)",
        prn=_on_synack,
        store=False,
        iface=iface,
    )
    _sniffer.start()
    print(f"[Locust] SYN-ACK sniffer started on {iface} for {TARGET_HOST}:{TARGET_PORT}")

@events.quitting.add_listener
def _stop_sniffer(**kwargs):
    global _sniffer
    if _sniffer:
        _sniffer.stop()
        _sniffer = None
        print("[Locust] SYN-ACK sniffer stopped")

class UserClass(User):
    wait_time = constant(0)
    source_ip = None

    def on_start(self):
        _load_pool()
        if not _ip_pool:
            raise Exception("IP pool is empty — check IP_POOL_FILE")
        self.source_ip = random.choice(_ip_pool)
        _start_sniffer()

    @task
    def keep_send(self):

        start = time.perf_counter()
        try:
            tcp_packet(dst_port=TARGET_PORT, src_ip=self.source_ip)
            rt = (time.perf_counter() - start) * 1000

            last: Optional[float] = _last_synack
            if last is None:
                exception = None
            elif (time.time() - last) > SYNACK_TIMEOUT:
                exception = Exception("No SYN-ACK received")
            else:
                exception = None

            self.environment.events.request.fire(
                request_type="TCP",
                name="tcp_flood",
                response_time=rt,
                response_length=0,
                exception=exception,
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

