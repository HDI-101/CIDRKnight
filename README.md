# CIDRKnight

CIDRKnight is a Python-based network reconnaissance tool that performs ICMP host discovery and multithreaded TCP port scanning on **CIDR subnets**. It generates structured JSON and Markdown reports for easy analysis.

---

## Features

- Accepts CIDR subnet input (e.g., `192.168.1.0/24`)  
- ICMP-based live host discovery  
- Multithreaded TCP port scanning  
- JSON output format (`scan_results.json`)  
- Automated Markdown report generation (`scan_report.md`)  
- Cross-platform support (Linux / Windows)

---

## Installation

### Python

Ensure Python 3.8+ is installed:

```bash
python --version
```

---

## Setup & Usage

Clone the repository and navigate to the project folder:

```bash
git clone https://github.com/HDI-101/CIDRKnight.git
cd CIDRKnight
```

Run the Script:

```bash
python3 CIDRKnight.py <CIDR>
```

Example:

```bash
python CIDRKnight.py 192.168.1.0/24
```

