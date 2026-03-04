import argparse
import ipaddress
import subprocess
import platform
import socket
import json
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime

COMMON_PORTS = [
    21, 22, 23, 25, 53, 80, 110, 111, 135, 139,
    143, 443, 445, 993, 995, 1723, 3306, 3389,
    5900, 8080
]

def ping_host(ip):
    param = "-n" if platform.system().lower() == "windows" else "-c"
    command = ["ping", param, "1", str(ip)]
    result = subprocess.run(command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return result.returncode == 0

def discover_live_hosts(network):
    live_hosts = []
    with ThreadPoolExecutor(max_workers=100) as executor:
        futures = {executor.submit(ping_host, ip): ip for ip in network.hosts()}
        for future in as_completed(futures):
            ip = futures[future]
            try:
                if future.result():
                    live_hosts.append(str(ip))
            except:
                pass
    return live_hosts

def scan_port(ip, port):
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)
        result = sock.connect_ex((ip, port))
        sock.close()
        return port if result == 0 else None
    except:
        return None

def scan_ports(ip):
    open_ports = []
    with ThreadPoolExecutor(max_workers=100) as executor:
        futures = {executor.submit(scan_port, ip, port): port for port in COMMON_PORTS}
        for future in as_completed(futures):
            port = future.result()
            if port:
                open_ports.append(port)
    return sorted(open_ports)

def generate_markdown(results):
    filename = "scan_report.md"
    with open(filename, "w") as f:
        f.write("# Network Scan Report\n\n")
        f.write(f"Generated on: {datetime.now()}\n\n")
        for ip, ports in results.items():
            f.write(f"## {ip}\n")
            if ports:
                for port in ports:
                    f.write(f"- Port {port} is open\n")
            else:
                f.write("No open common ports found.\n")
            f.write("\n")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("cidr", help="CIDR subnet (e.g., 192.168.1.0/24)")
    args = parser.parse_args()

    network = ipaddress.ip_network(args.cidr, strict=False)

    print("Discovering live hosts...")
    live_hosts = discover_live_hosts(network)

    results = {}

    print("Scanning ports...")
    for ip in live_hosts:
        open_ports = scan_ports(ip)
        results[ip] = open_ports

    with open("scan_results.json", "w") as f:
        json.dump(results, f, indent=4)

    generate_markdown(results)

    print("Scan complete.")
    print("Output saved to scan_results.json and scan_report.md")

if __name__ == "__main__":
    main()