# locustfile.py
from gevent import monkey
monkey.patch_all()


import sys
import time
import socket
from typing import Optional

from locust import User, task, between, events, TaskSet

# ---------- kompatibilní wrapper pro eventy Locust ----------
def fire_request_event(success: bool, request_type: str, name: str, response_time: int,
                       response_length: int = 0, exception: Optional[Exception] = None):
    """
    Kompatibilní volání eventu pro různé verze Locustu.
    Pokusí se zavolat novější unified events.request nebo starší request_success/request_failure.
    """
    # new unified API: events.request.fire(...)
    if hasattr(events, "request"):
        try:
            # preferovaná varianta s pojmenovanými argumenty
            events.request.fire(request_type, name, response_time, response_length, exception=exception, success=success)
            return
        except TypeError:
            try:
                # fallback: některé starší drobné verze mohou mít jiný podpis
                events.request.fire(request_type, name, response_time, response_length, exception, success)
                return
            except Exception:
                pass

    # fallback to older separate events
    if success and hasattr(events, "request_success"):
        try:
            events.request_success.fire(request_type=request_type, name=name, response_time=response_time, response_length=response_length)
            return
        except Exception:
            pass
    if (not success) and hasattr(events, "request_failure"):
        try:
            events.request_failure.fire(request_type=request_type, name=name, response_time=response_time, exception=exception)
            return
        except Exception:
            pass
    # pokud nic nefunguje, ticho — nechceme crashovat z důvodu telemetry

# ---------- TCP klient ----------
class GeventTcpClient:
    def __init__(self, host: str, port: int, timeout: float = 5.0):
        self.host = host
        self.port = port
        self.timeout = timeout
        self.sock: Optional[socket.socket] = None

    def connect(self) -> bool:
        start = time.time()
        try:
            self.sock = socket.create_connection((self.host, self.port), timeout=self.timeout)
            elapsed = int((time.time() - start) * 1000)
            fire_request_event(True, "tcp", "connect", elapsed, response_length=0)
            return True
        except Exception as e:
            elapsed = int((time.time() - start) * 1000)
            fire_request_event(False, "tcp", "connect", elapsed, exception=e)
            self.sock = None
            return False

    def send_and_recv(self, data: bytes, recv_buf: int = 4096):
        if not self.sock:
            raise RuntimeError("Socket not connected")
        start = time.time()
        try:
            self.sock.sendall(data)
            try:
                resp = self.sock.recv(recv_buf)
            except socket.timeout:
                resp = b""
            elapsed = int((time.time() - start) * 1000)
            fire_request_event(True, "tcp", "send_recv", elapsed, response_length=len(resp))
            return resp
        except Exception as e:
            elapsed = int((time.time() - start) * 1000)
            fire_request_event(False, "tcp", "send_recv", elapsed, exception=e)
            return None

    def close(self):
        if self.sock:
            try:
                self.sock.close()
            except Exception:
                pass
            self.sock = None

# ---------- Locust TaskSet ----------
class TcpBehavior(TaskSet):
    payload = b"Test 12345"
    count = 100
    delay = 0.01
    reuse_connection = True

    @task
    def send_payloads(self):
        user: "TcpUser" = self.user  # type: ignore
        client: Optional[GeventTcpClient] = getattr(user, "tcp_client", None)
        if client is None:
            client = GeventTcpClient(host=user.host, port=user.tcp_port, timeout=3)
            user.tcp_client = client
            if not client.connect():
                return

        if self.reuse_connection:
            if not client.sock:
                if not client.connect():
                    return
            for i in range(1, self.count + 1):
                client.send_and_recv(self.payload)
                time.sleep(self.delay)
        else:
            for i in range(1, self.count + 1):
                if not client.connect():
                    continue
                client.send_and_recv(self.payload)
                client.close()
                time.sleep(self.delay)

# ---------- Locust User ----------
class TcpUser(User):
    tasks = [TcpBehavior]
    wait_time = between(1, 2)

    host: str = "192.168.112.129"
    tcp_port: int = 12345

    def __init__(self, environment):
        super().__init__(environment)
        self.tcp_client = GeventTcpClient(host=self.host, port=self.tcp_port, timeout=3)

        # default behaviour (overrideable)
        TcpBehavior.payload = b"hello\n"
        TcpBehavior.count = 100
        TcpBehavior.delay = 0.01
        TcpBehavior.reuse_connection = True

    def on_start(self):
        if TcpBehavior.reuse_connection:
            self.tcp_client.connect()

    def on_stop(self):
        self.tcp_client.close()

def run_once(host: str, tcp_port: int, payload: bytes, count: int, delay: float, reuse_connection: bool):
    print("RUN_ONCE START")
    print("python executable:", sys.executable)
    print("target:", host, tcp_port, "count=", count, "delay=", delay, "reuse=", reuse_connection)
    client = GeventTcpClient(host=host, port=tcp_port, timeout=5)
    print("Connecting...")
    if not client.connect():
        print("Connect failed, končím.")
