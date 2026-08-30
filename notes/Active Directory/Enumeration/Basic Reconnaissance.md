
## 1. Host Discovery

First, identify **live hosts** in the target subnet.

### fping
```bash
fping -agq 10.211.11.0/24
```
- `-a` → Show only alive hosts.
- `-g` → Generate targets from the subnet.
- `-q` → Quiet output.

### Nmap
```bash
nmap -sn 10.211.11.0/24
```
- `-sn` → Host discovery only; doesn't perform port scanning.
    

---

# 2. Identify the Domain Controller

Important AD ports:

|    Port | Service     | Purpose                       |
| ------: | ----------- | ----------------------------- |
|  **88** | Kerberos    | AD authentication             |
| **135** | MS-RPC      | RPC enumeration               |
| **139** | NetBIOS/SMB | Legacy SMB                    |
| **389** | LDAP        | AD queries                    |
| **445** | SMB         | File sharing & AD enumeration |
| **464** | Kerberos    | Password changes              |
|     636 | LDAPS       | Encrypted LDAP                |

### Targeted Nmap Scan
```bash
nmap -p 88,135,139,389,445,636 -sV -sC -iL hosts.txt
```
- `-p` → Scan specific AD-related ports.
- `-sV` → Detect service versions.
- `-sC` → Run default NSE scripts.
- `-iL hosts.txt` → Read targets from a file.
    

**DC indicator:**
```text
88 (Kerberos)
389 (LDAP)
445 (SMB)
```
A host exposing these services is likely to be a **Domain Controller**.

---
# 3. Full Port Scan

For a more complete assessment:
```bash
nmap -sS -p- -T3 -iL hosts.txt -oN full_port_scan.txt
```
- `-sS` → TCP SYN scan.
- `-p-` → Scan all 65,535 ports.
- `-T3` → Normal scan speed.
- `-iL` → Read targets from `hosts.txt`.
- `-oN` → Save results to a file.
    
---

## DNS Enumeration

it is worth performing basic DNS enumeration to identify key services in the AD environment. DNS is the backbone of AD. Domain controllers, mail servers, and other critical infrastructure are all registered as DNS records. A few useful lookups include:

```bash
# Identify domain controllers via SRV records
nslookup -type=SRV _ldap._tcp.dc._msdcs.thm.loc 192.168.12.100

# Identify the Kerberos KDC
nslookup -type=SRV _kerberos._tcp.thm.loc 192.168.12.100

# Identify mail servers
nslookup -type=MX thm.loc 192.168.12.100
    
```

