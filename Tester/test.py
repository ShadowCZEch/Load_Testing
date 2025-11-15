open_ports = connect_scan(dst_ip, ports, timeout=0.5, pause=0.01)
print("Otevřené porty:", open_ports)

if not open_ports:
    print("Žádné otevřené porty nalezeny")
    raise Exception
chosen = random.choice(open_ports)
print("Náhodně vybraný port:", chosen)