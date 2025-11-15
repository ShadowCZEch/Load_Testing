from Procedures import connect_scan, TCP_send, check_tcp_port
from Config_Load import config_load
from Procedures import TCP_send
from Connection import tcp_scan, udp_scan


if __name__ == "__main__":
    tcp_scan()
    udp_scan()
