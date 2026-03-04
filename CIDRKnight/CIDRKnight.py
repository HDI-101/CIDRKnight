"""
CIDRKnight.py
Author: Hadi Taha

Description:
CIDRKnight is a Python tool for scanning a CIDR subnet.
It discovers live hosts via ICMP ping and performs TCP port scanning.
Generates output in JSON and Markdown formats.

Requirements:
- Python 3.8+
"""

import argparse
import ipaddress
import subprocess
import platform
import socket
import json
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime

# Common TCP ports to scan
COMMON_PORTS = [
    21, 22, 23, 25, 53, 80, 110, 111, 135, 139,
    143, 443, 445, 993, 995, 1723, 3306, 3389,
    5900, 8080
]

def ping_host(ip):
    """
    Ping an IP address to check if it is alive.

    Args:
        ip (str): IP address to ping.

    Returns:
        bool: True if host responds to ping, False otherwise.
    """
    param = "-n" if platform.system().lower() == "windows" else "-c"
    command = ["ping", param, "1", str(ip)]
    result = subprocess.run(command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return result.returncode == 0

def discover_live_hosts(network):
    """
    Discover all live hosts in a CIDR network using multithreading.

    Args:
        network (ipaddress.IPv4Network): CIDR network to scan.

    Returns:
        list: List of live host IPs as strings.
    """
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
    """
    Scan a single TCP port on a given IP address.

    Args:
        ip (str): IP address to scan.
        port (int): TCP port number.

    Returns:
        int or None: Port number if open, None otherwise.
    """
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)
        result = sock.connect_ex((ip, port))
        sock.close()
        return port if result == 0 else None
    except:
        return None

def scan_ports(ip):
    """
    Scan common TCP ports on a live host using multithreading.

    Args:
        ip (str): IP address of the live host.

    Returns:
        list: Sorted list of open ports.
    """
    open_ports = []
    with ThreadPoolExecutor(max_workers=100) as executor:
        futures = {executor.submit(scan_port, ip, port): port for port in COMMON_PORTS}
        for future in as_completed(futures):
            port = future.result()
            if port:
                open_ports.append(port)
    return sorted(open_ports)

def generate_markdown(results):
    """
    Generate a Markdown report summarizing scan results.

    Args:
        results (dict): Dictionary with IPs as keys and list of open ports as values.

    Output:
        Creates 'scan_report.md' file in current directory.
    """
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
    """
    Main function to parse arguments, perform host discovery and port scanning,
    and save results to JSON and Markdown files.
    """
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