After compromising a host, **enumerate the network before moving laterally**. Identify reachable hosts, IPs, DNS servers, and open ports.

### Enumeration Methods

Preferred order:

1. **Existing information**
    - ARP cache
    - Hosts file
    - DNS configuration
2. **Pre-installed tools** 
3. **Static binaries** — tools with dependencies compiled in — e.g. `nmap` compiled version
4. **Shell/script-based enumeration**
5. **Local tools through a proxy** — slow; use as a last resort

This approach is an example of **Living off the Land (LotL)**: using tools already available on the compromised system.

### Useful Information

**Linux:**
```bash
arp -a
cat /etc/hosts
cat /etc/resolv.conf
nmcli dev show
```

**Windows:**
```cmd
arp -a
type C:\Windows\System32\drivers\etc\hosts
ipconfig /all
```

### Ping Sweep

If `nmap` is unavailable, Bash can be used:
```bash
for i in {1..255}; do (ping -c 1 192.168.1.$i | grep "bytes from" &); done
```

This sends ICMP requests in parallel and displays responding hosts.

### Static Binaries

A **static binary** contains its required libraries inside the executable, so it can run without the target having those dependencies installed.

Useful when:
- Required tools are not installed.
- You cannot install packages.
- You need a portable version of a tool.

### Port Scanning Without Tools

Bash can check TCP ports using `/dev/tcp`:
```bash
for i in {1..65535}; do
    (echo > /dev/tcp/192.168.1.1/$i) >/dev/null 2>&1 && echo "$i is open"
done
```

 Full 65,535-port scans this way are **very slow**.

### Scanning Through a Proxy

Tools such as `proxychains` can scan through a compromised host, but this is usually slow and limited.

A better approach:
```text
Compromised Host
      │
      ├── Discover hosts
      ├── Identify open ports
      ↓
Use local tools through proxy
      ↓
Enumerate specific services
```

For example, use a static `nmap` on the compromised host for basic discovery, then use your local `nmap` through the proxy for more advanced enumeration such as **NSE scripts**.

### ICMP Blocked?

A host may be alive but not respond to ping because of firewall rules.

If ICMP fails, check common TCP ports instead.

**Key idea:**

> Enumerate the network from the compromised host first, then identify reachable systems and services that can be used for lateral movement.