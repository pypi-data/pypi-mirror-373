# 👻 GhostPeek

![GhostPeek Banner](https://img.shields.io/badge/GhostPeek-Domain%20Reconnaissance-blue?style=for-the-badge)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python](https://img.shields.io/badge/python-v3.6+-blue.svg)](https://www.python.org/downloads/)

**GhostPeek is a stealthy domain reconnaissance tool that silently collects intelligence on web domains.** Like a ghost, it reveals hidden digital footprints without drawing attention.

## What is GhostPeek and it's Features?

GhostPeek is a Python tool I made to learn more about web domains. Give it a domain name, and it will quietly gather all sorts of interesting information:

- 🔍 **Subdomain Discovery** - Finds subdomains you didn't know existed
- ℹ️ **WHOIS Intelligence** - Shows domain ownership and registration details  
- 🌐 **DNS Mapping** - Maps out all DNS records (A, NS, MX, CNAME, etc.)
- 🖥️ **IP Resolution** - Discovers IP addresses and ASN information
- 🔧 **Technology Detection** - Identifies web technologies and frameworks
- 📸 **Visual Screenshots** - Captures website screenshots automatically
- 📊 **HTML Reports** - Generates comprehensive, browsable reports
- ⚡ **Multi-threading** - Fast concurrent scanning
- 🎨 **Rich Terminal UI** - Beautiful command-line interface

## Why I Made This

I created GhostPeek as a personal project to learn more about how websites are structured and to practice my Python skills. It combines a bunch of different tools into one simple command, saving you time when you want to check out a website's technical details. Make sure to retry again in few mins if it catches 0 subdomains. 

## 🚀 Quick Start

### Installation

```bash
pip install ghostpeek
```

### One-Line Installation

```bash
# User installation
curl -sSL https://raw.githubusercontent.com/kaizoku73/Ghostpeek/main/install.sh | bash

# System-wide installation (requires sudo)
curl -sSL https://raw.githubusercontent.com/kaizoku73/Ghostpeek/main/install.sh | sudo bash

# After installation, simply run:
ghostpeek -d example.com
```

### Manual Installation

```bash
# Clone the repo
git clone https://github.com/kaizoku73/Ghostpeek.git
cd ghostpeek

# Install requirements
pip install -r requirements.txt
```

### Requirements

- Python 3.6+
- requests
- dnspython
- python-whois
- rich
- selenium
- python-Wappalyzer
- setuptools

## Basic Usage

```bash
# Scan a domain
python ghostpeek.py -d example.com

# Interactive mode
python ghostpeek.py

# Custom output directory
python ghostpeek.py -d example.com -o /path/to/output

# Adjust threading
python ghostpeek.py -d example.com -t 20

# Disable threading for sequential processing
python ghostpeek.py -d example.com --no-threading
```

### Options

```
-d, --domain    Target domain to investigate
-o, --output    Custom output directory (optional)
-t, --threads   Number of threads to use (default: 10)
--no-threading  Disable threading for sequential processing
```

## Example Output

When you run GhostPeek, you'll see a beautiful ASCII banner followed by real-time scanning progress:


```
▄████ ██░ ██ ▒█████ ██████ ▄▄▄█████▓ ██▓███ ▓█████ ▓█████ ██ ▄█▀
██▒ ▀█▒▓██░ ██▒▒██▒ ██▒▒██ ▒ ▓ ██▒ ▓▒▓██░ ██▒▓█ ▀ ▓█ ▀ ██▄█▒
...

Give your desire domain: example.com
Your secrets will be stored in: recon_example.com_20250825_143022

✓ Revealing WHOIS secrets for example.com
✓ Hunting for subdomains of example.com
✓ Found 15 unique domains
✓ Unmasking domains and resolving IPs
✓ Decoding DNS secrets
✓ Identifying technology fingerprints
✓ Capturing visual evidence

Mission accomplished! 🎉
Your intelligence report awaits: recon_example.com_20250825_143022/report.html
```

## The HTML Report

After GhostPeek finishes, it will automatically open an HTML report in your browser with tabs for:

- **📊 Overview** - Summary of findings and key metrics
- **ℹ️ WHOIS Details** - Domain registration and ownership info
- **🔍 Subdomains** - Complete list of discovered subdomains
- **🌐 DNS Records** - Detailed DNS information for each domain
- **🔧 Technologies** - Identified web technologies and frameworks
- **📸 Screenshots** - Visual captures of all accessible websites

## Disclaimer

**This tool is designed for educational purposes and authorized security testing only.**

- Only scan domains you own or have explicit permission to test
- Respect robots.txt and website terms of service  
- Be mindful of rate limiting to avoid overwhelming target servers
- Use responsibly and ethically

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🔗 Connect

- **Author**: kaizoku73
- **GitHub**: [@kaizoku73](https://github.com/kaizoku73)

---

<div align="center">
Made with ❤️ by kaizoku | ⭐ Star this repo if you found it helpful!
</div>
