from scapy.layers.inet import IP,TCP
from scapy.layers.inet6 import IPv6
from scapy.all import  sr1
import time
import socket
import traceback
from contextlib import closing


def check_tcp_port(host= "192.168.112.129", port = 44253, timeout=2.0):
    try:
        with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as s:
            s.settimeout(timeout)
            s.connect((host, port))
            print("Port naslouchá")
            return "open"
    except socket.timeout:
        print("Timeout")
        return "timeout"
    except ConnectionRefusedError:
        print("Refused")
        return "closed"
    except OSError as e:
        # síťové chyby jako síť nedosažitelná, nepřidělená adresa atd.
        return f"os error: {e}"
    except Exception as e:
        # neočekávané chyby
        return f"other error: {e}\n{traceback.format_exc()}"

if __name__ == "__main__":
    target = "192.168.112.129"
    ports = [12345]
    for p in ports:
        status = check_tcp_port(target, p, timeout=1.0)
        print(f"{target}:{p} -> {status}")

def connect_scan(dst_ip = "192.168.112.129", ports=range(12345), timeout=0.5, pause=0.01):
    open_ports = []
    for port in ports:
        with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as s:
            s.settimeout(timeout)
            try:
                s.connect((dst_ip, port))
                open_ports.append(port)
            except (ConnectionRefusedError, OSError):
                pass
            except socket.timeout:
                pass
        time.sleep(pause)
    return open_ports

def TCP_sendI():
    dst_ip = "192.168.112.129"
    ports = range(12345)

    syn = IP(dst=dst_ip) / TCP(dport=ports, flags="S", seq=100)
    resp = sr1(syn, timeout=2, verbose=True)
    if resp is None:
        print("Žádná odpověď")
    elif resp.haslayer(TCP) and resp[TCP].flags & 0x12:  # SYN+ACK = 0x12
        print("Port otevřen (SYN+ACK)")
    else:
        print("Jiná odpověď:", resp.summary())


def make_packet(payload, packet_size, pad_byte=b" "):
    """
    Vrátí bytes délky packet_size.
    - payload: bytes nebo str
    - packet_size: int > 0
    - pad_byte: single-byte bytes použité k doplnění (default mezera)
    Chování: pokud payload kratší -> opakuje payload dokud není dost; pokud payload delší -> truncate.
    """
    if isinstance(payload, str):
        data = payload.encode()
    else:
        data = payload

    if packet_size <= 0:
        raise ValueError("packet_size musí být kladné celé číslo")

    if len(data) == packet_size:
        return data
    if len(data) > packet_size:
        return data[:packet_size]
    # len(data) < packet_size: opakovat payload a případně doplnit pad_byte
    repeats = packet_size // len(data)
    remainder = packet_size % len(data)
    result = data * repeats + data[:remainder]
    # pokud bys chtěl jiný typ doplnění (např. nulami), použij pad_byte:
    # result = data + pad_byte * (packet_size - len(data))
    return result

def TCP_send(dst_ip="192.168.112.129", dst_port=12345, payload=b"Test 12345",
             count=100, delay=0.01, reuse_connection=True, timeout=2, packet_size=2048):
    # 1) SYN scan pomocí Scapy (kontrola, že port odpovídá SYN+ACK)
    syn = IP(dst=dst_ip) / TCP(dport=dst_port, flags="S", seq=100)
    resp = sr1(syn, timeout=timeout, verbose=False)
    if resp is None:
        print("Žádná odpověď (port uzavřen nebo filtrovaný).")
        return False
    if resp.haslayer(TCP) and (resp[TCP].flags & 0x12):  # SYN+ACK
        print(f"Port {dst_port} otevřen (SYN+ACK). Pokračuji v odesílání payloadů.")
        # poslat RST, abychom ukončili poloviční spojení z Scapy (nechceme ho držet)
        rst = IP(dst=dst_ip) / TCP(dport=dst_port, flags="R", seq=resp.ack)
        # send() může vyžadovat root; tady jen pokus o uklidnění stavu
        try:
            from scapy.all import send
            send(rst, verbose=False)
        except Exception:
            pass
    else:
        print("Jiná odpověď:", resp.summary())
        return False

    # 2) Odesílání payloadů: použijeme standardní Python socket (spolehlivější pro TCP stream)
    sent = 0
    if reuse_connection:
        # otevřít jedno spojení a poslat count payloadů v něm
        try:
            s = socket.create_connection((dst_ip, dst_port), timeout=5)
        except Exception as e:
            print("Nelze vytvořit TCP spojení:", e)
            return False
        try:
            for i in range(1, count + 1):
                try:
                    s.sendall(payload if isinstance(payload, bytes) else payload.encode())
                    sent += 1
                    print(f"{i}/{count} sent")
                except Exception as e:
                    print(f"{i}/{count} send failed: {e}")
                time.sleep(delay)
        finally:
            s.close()
    else:
        # pro každý payload nové spojení
        for i in range(1, count + 1):
            try:
                s = socket.create_connection((dst_ip, dst_port), timeout=5)
                s.sendall(payload if isinstance(payload, bytes) else payload.encode())
                s.close()
                sent += 1
                print(f"{i}/{count} sent")
            except Exception as e:
                print(f"{i}/{count} failed: {e}")
            time.sleep(delay)

    print(f"Odesláno {sent}/{count} payloadů na {dst_ip}:{dst_port}")
    return True

if __name__ == "__main__":
    # příklad volání
    TCP_send(dst_ip="192.168.112.129", dst_port=12345, payload="Test 12345",
             count=10000, delay=0.001, reuse_connection=True, packet_size=2048)