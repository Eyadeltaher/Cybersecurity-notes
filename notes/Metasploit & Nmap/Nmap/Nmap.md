
**nmap** is Network Mapper used for network discovery and security auditing. Nmap can be used for enumeration to identify open ports and services. **Enumeration** in Cybersecurity is information gathering technique.

![[Pasted image 20260503001737.png]]

Note --> If a host doesn’t respond, it’s marked as “down.” This is why you sometimes need **_-Pn_**— to tell Nmap _not_ to ping first (useful for CTFs where ICMP is blocked).

## Host Discovery
```bash
# Active host, network discovery
sudo nmap -sn 10.10.0.0/24

# Scan all ports, takes longer.
sudo nmap -p- <target-ip-addr>

# Scan top-ports for n number
nmap 10.112.158.102 --top-ports 1000
```

==NOTE== --> Run this command with the -vv switch enabled. It's good practice to _always_ increase the verbosity in your scans.
## Port Scanning Techniques

- **_-sS_**: **SYN scan (stealth)**
	- Sends a SYN, waits for SYN-ACK. Doesn’t complete the handshake — sneaky and fast.
- **_-sT_**: **TCP connect scan**
	- Completes the 3-way handshake. More detectable, but works when raw sockets aren’t allowed.
- **_-sU_**: **UDP scan**
	- Fires a UDP packet and hopes for a response. If there’s silence or ICMP “port unreachable,” it guesses the state.

## Version & OS Detection

- **_sV_**: Sends protocol-specific packets to grab **service banners**, then matches them to a DB.
- **_-O_**: Sends oddball TCP/IP packets to identify the OS stack based on how it responds (TTL values, TCP window size, etc.)

## NSE Scripts

The **Nmap Scripting Engine** (NSE) uses Lua scripts that plug into different phases of the scan.
```bash
# Performs a script scan using the default set of scripts
sudo nmap -sC <target-ip-addr>
```

You can:

- Enumerate usernames with **smb-enum-users**
- Bruteforce logins with **http-brute**
- Detect vulns with **— script vuln**

Each script belongs to categories like:
- **auth**, **vuln**, **default**, **discovery**, **brute**, etc.




---
# 1. Host discovery

### `-sn` — Ping scan

Checks whether hosts are alive **without doing a port scan**.

```bash
nmap -sn 192.168.1.0/24
```

Useful for finding live machines on a network.

### `-iL <file>` → I have a list of targets

Use this when your targets are already collected in a file.

```bash
nmap -iL targets.txt
```

---

### `-Pn` — Skip host discovery

Treat the target as online even if it doesn't respond to ping.

```bash
nmap -Pn 192.168.1.10
```

Very useful when ICMP/ping is blocked.

---

# `-PS` → TCP SYN host discovery

```bash
nmap -PS80,443 192.168.1.10
```

Instead of asking:

> "Does ICMP ping work?"

you ask:

> "Does the host respond to a TCP SYN?"

For example:

```
SYN → 192.168.1.10:443
```

If the host responds, Nmap can infer that the host is alive.

### When useful?

When:

```
ICMP → blocked
TCP → allowed
```

---

# `-PA` → TCP ACK discovery

```bash
nmap -PA80,443 192.168.1.10
```

Similar idea to `-PS`, but uses **ACK packets**.

### When?

Useful when you're dealing with filtering/firewall behavior where ACK-based probes may get a different response.

You won't use this nearly as often as:

```
-sn
-PS
-Pn
```

but it's useful when troubleshooting why host discovery isn't working.

---

# `-PU` → UDP discovery

```bash
nmap -PU53 192.168.1.10
```

Uses UDP probes.

### When?

When TCP/ICMP discovery isn't giving you useful results.

For example, you suspect the network has:

```
UDP 53 → DNS
UDP 161 → SNMP
```

You could use:

```bash
nmap -PU53,161 192.168.1.10
```

This is particularly relevant when assessing environments where UDP services are important.

---

# `-PE` → ICMP Echo

```bash
nmap -PE 192.168.1.10
```

This is basically the classic:

```bash
ping 192.168.1.10
```

concept.

### When?

Use it when normal ICMP echo discovery is appropriate.

For example:

```bash
nmap -PE 192.168.1.0/24
```

You're essentially asking:

> "Which hosts respond to ICMP Echo?"

---

# `-PP` → ICMP Timestamp

```bash
nmap -PP 192.168.1.10
```

This uses an ICMP timestamp request instead of an echo request.

### Why?

Some hosts/firewalls may block:

```
ICMP Echo
```

but respond to another ICMP type.

So `-PP` is more of a **fallback/alternative discovery technique**.

You generally won't start with it.

---

# `-PM` → ICMP Address Mask

```bash
nmap -PM 192.168.1.10
```

Another alternative ICMP discovery technique.

### When?

Mostly when you're experimenting with host discovery or dealing with unusual network behavior.

It's **not something you normally need in a basic pentest**.

---

# 2. Port scanning

### `-p` — Specify ports

Scan a specific port:

```bash
nmap -p 80 192.168.1.10
```

Multiple ports:

```bash
nmap -p 22,80,443 192.168.1.10
```

Port range:

```bash
nmap -p 1-1000 192.168.1.10
```

All TCP ports:

```bash
nmap -p- 192.168.1.10
```

`-p-` is essentially:

```text
1 → 65535
```

---

### `-F` — Fast scan

Scans fewer ports than the default scan.

```bash
nmap -F 192.168.1.10
```

Good for a quick initial check.

---

# 3. Service detection

This is the one you mentioned:

### `-sV` — Service/version detection

```bash
nmap -sV 192.168.1.10
```

Instead of simply telling you:

```text
80/tcp open
```

Nmap tries to determine **what service and version** are running:

```text
PORT   STATE SERVICE VERSION
22/tcp open  ssh     OpenSSH 9.9
80/tcp open  http    Apache httpd 2.4.62
```

This is extremely useful during enumeration because the version can help you identify potential vulnerabilities.

### `-sV` does NOT mean:

> "Scan all vulnerabilities."

It means:

> **"Try to identify the service and its version."**

---

# 4. Scan types

### `-sS` — SYN scan

```bash
sudo nmap -sS 192.168.1.10
```

One of the most commonly used TCP scan types.

Conceptually:

```text
Nmap                 Target
  │                     │
  │──── SYN ──────────>│
  │<─── SYN/ACK ───────│
  │──── RST ──────────>│
```

Nmap can determine that the port is open without completing a normal TCP connection.

Usually requires root/admin privileges.

---

### `-sT` — TCP Connect scan

```bash
nmap -sT 192.168.1.10
```

Uses the operating system's normal TCP connection mechanism.

Useful when SYN scanning isn't available.

---

### `-sU` — UDP scan

```bash
sudo nmap -sU 192.168.1.10
```

Scans UDP ports.

Useful for discovering things like:

```text
53   DNS
67   DHCP
69   TFTP
123  NTP
161  SNMP
```

UDP scanning can be significantly slower than TCP scanning.

---

### `-sA` — ACK scan

```bash
sudo nmap -sA 192.168.1.10
```

Primarily used to determine **firewall filtering behavior**, rather than discovering open ports directly.

---

# 5. OS detection

### `-O` — Operating system detection

```bash
sudo nmap -O 192.168.1.10
```

Nmap attempts to determine the target's OS.

Example:

```text
OS details:
Linux 5.x
```

It uses characteristics of the target's network responses.

---

### `-A` — Aggressive scan

```bash
sudo nmap -A 192.168.1.10
```

This enables several detection features, including:

- OS detection
    
- Version detection
    
- Default NSE scripts
    
- Traceroute
    

Think:

```text
-A
 │
 ├── OS detection
 ├── Service/version detection
 ├── NSE scripts
 └── Traceroute
```

It's powerful but generates considerably more traffic than a basic scan.

---

# 6. NSE scripts

### `-sC` — Default scripts

```bash
nmap -sC 192.168.1.10
```

Runs Nmap's **default NSE scripts**.

NSE = **Nmap Scripting Engine**.

You can combine it with version detection:

```bash
nmap -sC -sV 192.168.1.10
```

This is one of the most useful enumeration commands.

---

### `--script`

Run a specific NSE script:

```bash
nmap --script <script> <target>
```

For example:

```bash
nmap --script http-title 192.168.1.10
```

Or a category:

```bash
nmap --script vuln 192.168.1.10
```
The `vuln` category contains scripts designed to check for certain known vulnerabilities and exposures. **Only use these against systems you're authorized to test

There are many categories available. Some useful categories include:

- `safe`:- Won't affect the target
- `intrusive`:- Not safe: likely to affect the target  
- `vuln`:- Scan for vulnerabilities
- `exploit`:- Attempt to exploit a vulnerability
- `auth`:- Attempt to bypass authentication for running services (e.g. Log into an FTP server anonymously)
- `brute`:- Attempt to bruteforce credentials for running services
- `discovery`:- Attempt to query running services for further information about the network (e.g. query an SNMP server).

A more exhaustive list can be found [here (opens in new tab)](https://nmap.org/book/nse-usage.html).

```bash
nmap --script "smb-*" 192.168.1.10
```
to try all smtp scripts on the target

Multiple scripts can be run simultaneously in this fashion by separating them by a comma. For example: `--script=smb-enum-users,smb-enum-shares`

Some scripts require arguments (for example, credentials, if they're exploiting an authenticated vulnerability). These can be given with the `--script-args` Nmap switch. An example of this would be with the `http-put` script (used to upload files using the PUT method). This takes two arguments: the URL to upload the file to, and the file's location on disk.  For example:

`nmap -p 80 --script http-put --script-args http-put.url='/dav/shell.php',http-put.file='./shell.php'`

Note that the arguments are separated by commas, and connected to the corresponding script with periods (i.e.  `<script-name>.<argument>`).

A full list of scripts and their corresponding arguments (along with example use cases) can be found [here (opens in new tab)](https://nmap.org/nsedoc/).

Nmap scripts come with built-in help menus, which can be accessed using `nmap --script-help <script-name>`. This tends not to be as extensive as in the link given above, however, it can still be useful when working locally. --> `nmap --script-help ftp-anon.nse`

## Search for script

`/usr/share/nmap/scripts/script.db` file. Despite the extension, this isn't actually a database so much as a formatted text file containing filenames and categories for each available script
For example: `grep "ftp" /usr/share/nmap/scripts/script.db`

The second way to search for scripts is quite simply to use the `ls` command. For example, we could get the same results as in the previous screenshot by using `ls -l /usr/share/nmap/scripts/*ftp*`



==NOTE ==--> do not try default scripts only go for all scripts of certian service

---

# 7. Timing

Nmap has timing templates:

```text
-T0
-T1
-T2
-T3
-T4
-T5
```

From slowest to fastest:

```text
T0 → T1 → T2 → T3 → T4 → T5
```

### `-T3`

Default/general-purpose timing.

```bash
nmap -T3 192.168.1.10
```

### `-T4`

Faster:

```bash
nmap -T4 192.168.1.10
```

Common in labs/CTFs.

### `-T5`

Very aggressive:

```bash
nmap -T5 192.168.1.10
```

Can be unreliable on slower networks.

---

# 8. Output

### `-oN` — Normal output

```bash
nmap -oN scan.txt 192.168.1.10
```

Save the scan as readable text.


# The practical decision tree

This is what I'd actually memorize:

```
                 START
                   │
                   ▼
          What are my targets?
                   │
       ┌───────────┴───────────┐
       │                       │
   Few targets             Many targets
       │                       │
       │                      -iL
       │                       │
       └───────────┬───────────┘
                   ▼
                   │
                   │
                   ▼
        Need to find live hosts?
                   │
                  -sn
                   │
                   ▼
       Discovery isn't working?
                   │
          ┌────────┼────────┐
          │        │        │
        -Pn      -PS      -PU
          │        │        │
       Known     TCP      UDP
       target   probing   probing
          │
          ▼
      Start port scan
```

Then DNS:

```
Do I need DNS names?

YES ──→ -R
 │
NO
 │
└────→ -n
```

And topology:

```
Want network path?
       │
       └──→ --traceroute
```