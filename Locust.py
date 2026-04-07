# locustfile.py

import os
from gevent import monkey
import time
from locust import User, task, events, constant
from gevent import sleep
from Config_Load import Config_Load

monkey.patch_all()

cfg = Config_Load()

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

TARGET_PORT = int(os.environ.get("TARGET_PORT", 0))
LOCUST_MODE = os.environ.get("LOCUST_MODE")

class UserClass(User):

    wait_time = constant(0)

    @task
    def keep_send(self):
        from Hook_system import fire_packet_event
        from Packet_create import tcp_packet, udp_packet

        if LOCUST_MODE == "tcp":
                start = time.perf_counter()
                try:
                    tcp_packet(dst_port=TARGET_PORT)
                    rt = (time.perf_counter() - start) * 1000
                    self.environment.events.request.fire(
                        request_type="TCP",
                        name="tcp_flood",
                        response_time=rt,
                        response_length=0,
                        exception=None,
                    )
                    fire_packet_event(self.environment,"TCP","tcp_sent",start)
                except Exception as e:
                    fire_packet_event(self.environment,"TCP","tcp_sent",start,exception=e)
                sleep(0)


        elif LOCUST_MODE == "udp":
                start = time.perf_counter()
                try:
                    udp_packet(dst_port=TARGET_PORT)
                    rt = (time.perf_counter() - start) * 1000
                    self.environment.events.request.fire(
                        request_type="UDP",
                        name="udp_flood",
                        response_time=rt,
                        response_length=0,
                        exception=None,
                    )
                    fire_packet_event(self.environment,"UDP","udp_sent",start)
                except Exception as e:
                    fire_packet_event(self.environment,"UDP","udp_sent",start,exception=e)
                sleep(0)

@events.test_start.add_listener
def on_test_start(environment, **_kwargs):
    host = environment.host
    mode = os.environ.get("LOCUST_MODE", "unknown")
    print(f"\n[locust] Test starting on {host} — mode: {mode.upper()}\n")

