import secrets
import ipaddress
import random
import psutil
from scapy.layers.inet6 import IPv6, ICMPv6ND_NS
from scapy.layers.l2 import Ether,ARP
from scapy.sendrecv import sr1,srp
from Config_Load import Config_Load


class IPGenerator:
    _instance = None
    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if hasattr(self, "_initialized") and self._initialized:
            return

        self.cfg = Config_Load()
        self.pick = int(self.cfg.data["pick"])
        self.unique_users_count = int(self.cfg.data["unique_users_count"])
        self.iface = self.linux_detect_iface()

        self.source_ip_minimal = self.cfg.data["source_ip_minimal"]
        self.source_ip_maximal = self.cfg.data["source_ip_maximal"]
        self.version_minimal = int(ipaddress.ip_address(self.source_ip_minimal))
        self.version_maximal = int(ipaddress.ip_address(self.source_ip_maximal))

        if self.version_minimal == 4 & self.version_maximal == 4:
            self.ip_min = int(ipaddress.IPv4Address(self.source_ip_minimal))
            self.ip_max = int(ipaddress.IPv4Address(self.source_ip_maximal))
            self.protocol = ipaddress.IPv4Address
        elif self.version_minimal == 6 & self.version_maximal == 6:
            self.ip_min = int(ipaddress.IPv6Address(self.source_ip_minimal))
            self.ip_max = int(ipaddress.IPv6Address(self.source_ip_maximal))
            self.protocol = ipaddress.IPv6Address
        else:
            raise ValueError("Invalid protocol value")

        self.check = self.ip_max - self.ip_min + 1

        if self.ip_min > self.ip_max:
            raise ValueError("Range error")

        if self.check < self.unique_users_count:
            raise ValueError("Too many users for selected range")

        self.generated = self.generate_ips()
        self._initialized = True


    def linux_detect_iface(self):
        for iface, addrs in psutil.net_if_addrs().items():
            if iface == "lo":
                continue
            if iface.startswith("docker") or iface.startswith("veth"):
                continue
            return self.iface
        raise RuntimeError("No valid interface found")

    def is_used(self,ip_str,protocol, iface):
            if protocol == 4:
                return self.is_IPv4_used_linux(ip_str, iface)
            else:
                return self.is_IPv6_used_linux(ip_str, iface)

    def is_IPv4_used_linux(self,ip,iface):
        arp = ARP(pdst=ip)
        ether = Ether(dst="ff:ff:ff:ff:ff:ff")
        ans = srp(ether/arp, timeout=1, iface=iface, verbose=False)[0]
        return len(ans) > 0

    def is_IPv6_used_linux(self,ip,iface):
        ns = IPv6(dst=ip)/ICMPv6ND_NS(tgt=ip)
        ans = sr1(ns, timeout=1, iface=iface, verbose=False)
        return ans is not None

    def generate_ips(self):
        gen = []
        tried = set()

        while len(gen) < self.unique_users_count:
            remaining = self.unique_users_count - len(gen)
            if self.protocol == 4:
                chosen = random.sample(range(self.ip_min, self.ip_max + 1), remaining)

            else:
                chosen_offset = set()
                while len(chosen_offset) < remaining:
                    offset = secrets.randbelow(self.check)
                    chosen_offset.add(self.ip_min + offset)
                chosen = list(chosen_offset)

            for generated in chosen:
                if len(gen) >= self.unique_users_count:
                    break
                elif generated in tried:
                    continue
                tried.add(generated)

                ip_str = str(self.protocol(generated))

                if self.is_used(ip_str, self.pick, self.iface):
                    continue
                gen.append(ip_str)

        return gen

    def get_ips(self):
        return self.generated