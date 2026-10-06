
Port forwarding is a pivoting technique that allows network packets to be relayed from a port to another. The tunnel can be setup between two controlled and connected machines, hence allowing a bridge between a network and another. That concept is similar to PAT (Port Address Translation), an extension of NAT (Network Address Translation) that allows multiple devices on a LAN to be mapped to a single public IP address by assigning addresses to ports numbers.

This technique is useful when an attacker wants to stay under the radar or when access to a service is limited to a specific network.
# Local Port Forward — `-L`

Suppose your network looks like this:
```text
Your AttackBox
192.168.13.50
      |
      | SSH
      ↓
Web Server / Pivot
192.168.13.71
      |
      | Internal network
      ↓
DC
192.168.13.100:3389
```

Your AttackBox **cannot directly reach** `192.168.13.100:3389`.

But the Web Server can.

So you create:
```bash
ssh -L 13389:192.168.13.100:3389 user@192.168.13.71 -N
```

This means:
```text
AttackBox                         Web Server                 DC
127.0.0.1:13389
      │
      │ SSH tunnel
      └──────────────────────────> 192.168.13.71
                                      │
                                      │ TCP connection
                                      └──────────────> 192.168.13.100:3389
```

Now, when you do:
```bash
xfreerdp /v:127.0.0.1:13389
```

you're **not actually connecting directly to `127.0.0.1:13389` as an RDP server**.

Instead:
```text
xfreerdp
   │
   │ connects to
   ↓
127.0.0.1:13389
   │
   │ SSH forwards it
   ↓
192.168.13.71
   │
   │ connects to
   ↓
192.168.13.100:3389
```

---

## 2. Understand the syntax

General syntax:
```bash
ssh -L <LOCAL_PORT>:<TARGET_HOST>:<TARGET_PORT> <USER>@<SSH_SERVER>
```

For your example:
```bash
ssh -L 13389:192.168.13.100:3389 user@192.168.13.71 -N
```

Break it down:

|Part|Meaning|
|---|---|
|`ssh`|Create an SSH connection|
|`-L`|Create a **local port forward**|
|`13389`|Port opened on **your AttackBox**|
|`192.168.13.100`|Final destination|
|`3389`|Final destination port (RDP)|
|`user@192.168.13.71`|SSH server/pivot|
|`-N`|Don't start a shell; only create the tunnel|

The important distinction is:

```text
LOCAL PORT          FINAL TARGET            PIVOT/SSH SERVER
   ↓                    ↓                         ↓
 13389          192.168.13.100:3389          192.168.13.71 
```

The **pivot doesn't have to be the final target**.

That's what makes it useful for pivoting.

---

## 3. Why `localhost`?

After running:
```bash
ssh -L 13389:192.168.13.100:3389 user@192.168.13.71 -N
```

SSH creates a listener on your machine:
```text
127.0.0.1:13389
```

You can verify it with:
```bash
ss -lntp | grep 13389
```

You should see something listening on that port.

So your tools don't need to understand SSH tunneling.

For example, instead of:
```bash
xfreerdp /v:192.168.13.100:3389
```

you use:
```bash
xfreerdp /v:127.0.0.1:13389
```

From the application's perspective, it's simply connecting to:
```text
localhost:13389
```

SSH handles the rest.

---

## 4. Why is it called **Local** Port Forward?

Because the listening port is created on the **local machine**.

```text
            LOCAL
          AttackBox
       127.0.0.1:13389
              │
              │ SSH
              ↓
        Pivot Server
              │
              ↓
       Internal Service
```

The direction is essentially:
```text
LOCAL PORT → SSH SERVER → TARGET
```

---

## 5. Example: MySQL

Imagine:
```text
   AttackBox
      |
      | SSH
      ↓ 
  Web Server
      |
      ↓
   Internal DB
10.10.20.15:3306
```

You want to access MySQL, but the database isn't reachable directly.

Create:
```bash
ssh -L 13306:10.10.20.15:3306 user@10.10.20.10 -N
```

Now:
```bash
mysql -h 127.0.0.1 -P 13306 -u root -p
```

Traffic becomes:
```text
mysql
  ↓
127.0.0.1:13306
  ↓
SSH tunnel
  ↓
10.10.20.10
  ↓
10.10.20.15:3306
```

---

# Dynamic forwarding `-D`

Turn your SSH connection into a flexible proxy that routes traffic dynamically to any destination, rather than mapping just one static port.
### `-L` vs `-D`

With `-L`, you decide **in advance** where the traffic goes:
```text
127.0.0.1:13389
       ↓
Pivot
       ↓
192.168.13.100:3389
```

With `-D`, you create a **SOCKS proxy**, and the application decides where the traffic goes:
```text
                    ┌──→ 192.168.13.100:3389
                    │
Tool → SOCKS → Pivot├──→ 192.168.13.101:22
                    │
                    └──→ 192.168.13.102:80
```

So:
> **`-L` = one specific destination**  
> **`-D` = many destinations dynamically**

---

## 1. The command

```bash
ssh -f -D 1080 user@192.168.13.71 -N
```

Let's break it down:

| Option               | Meaning                                   |
| -------------------- | ----------------------------------------- |
| `-D 1080`            | Create a SOCKS proxy on local port `1080` |
| `user@192.168.13.71` | SSH into the pivot                        |
| `-N`                 | Don't execute a remote command            |
| `-f`                 | Put SSH into the background               |

After running it, you have:
```text
AttackBox
127.0.0.1:1080
      │
      │ SOCKS
      ↓
192.168.13.71
      │
      ↓
Internal network
```

You can check:
```bash
ss -lntp | grep 1080
```

---

# 2. What does SOCKS actually do?

**SOCKS** (Socket Secure) is an internet protocol that routes network packets between a client and server through a proxy server. Unlike HTTP proxies (which only understand HTTP/HTTPS traffic), **SOCKS operates at Layer 5 (Session Layer)**, meaning it can proxy almost any TCP or UDP traffic (HTTP, SSH, FTP, custom tools).


Suppose your pivot can reach:
```text
192.168.13.100
192.168.13.101
192.168.13.102
```

but your AttackBox cannot.

You configure a tool to use:
```text
SOCKS5
127.0.0.1
1080
```

Then the tool says:
> "I want to connect to `192.168.13.100:80`."

The SOCKS proxy receives that request and SSH tells the pivot:
> "Connect to `192.168.13.100:80`."

The pivot makes the connection.
```text
AttackBox                         Pivot
    │                               │
    │ SOCKS request                 │
    │ 192.168.13.100:80             │
    ├──────────────────────────────>│
    │                               │
    │                               │──────> 192.168.13.100:80
    │                               │
    │<────────── traffic ───────────│
```

The important part is that **the pivot performs the final connection**.

---

# 3. Why is it "dynamic"?

Look at `-L`:
```bash
ssh -L 13389:192.168.13.100:3389 user@192.168.13.71 -N
```

You explicitly specify:
```text
192.168.13.100:3389
```

If you also want:
```text
192.168.13.101:22
```

you need another forward:
```bash
ssh -L 13389:192.168.13.100:3389 \
    -L 10022:192.168.13.101:22 \
    user@192.168.13.71 -N
```

With `-D`, you don't need to create a separate `-L` for every destination.

You create **one proxy**:
```bash
ssh -D 1080 user@192.168.13.71 -N
```

Then applications can request different destinations through it:
```text
SOCKS :1080
    │
    ├──→ 192.168.13.100:3389
    ├──→ 192.168.13.101:22
    ├──→ 192.168.13.102:80
    └──→ 192.168.13.103:445
```
That's why it's called **dynamic**.

---

# 4. Practical example with a browser

Imagine the internal network has:
```text
192.168.13.100:80   → Internal Web Server
192.168.13.101:80   → Admin Panel
192.168.13.102:80   → Another Web Server
```

Your AttackBox cannot access them directly.

Create:
```bash
ssh -D 1080 user@192.168.13.71 -N
```

Configure your browser:
```text
SOCKS5
Host: 127.0.0.1
Port: 1080
```

Then browse to:
```text
http://192.168.13.100
```

The traffic becomes:
```text
Browser
   │
   │ SOCKS5
   ↓
127.0.0.1:1080
   │
   │ SSH
   ↓
192.168.13.71
   │
   ├────→ 192.168.13.100:80
   │
   ├────→ 192.168.13.101:80
   │
   └────→ 192.168.13.102:80
```

You didn't create three tunnels.

You created **one SOCKS tunnel**.

---

# 5. Using it with proxy-aware tools

For example, with `proxychains` you can configure:
```text
socks5 127.0.0.1 1080
```

Then:
```bash
proxychains nmap ...
```

or:
```bash
proxychains curl http://192.168.13.100
```

The idea is:
```text
Application
     ↓
Proxychains
     ↓
SOCKS5 :1080
     ↓
SSH tunnel
     ↓
Pivot
     ↓
Internal target
```

**Important:** not every tool works correctly through SOCKS/proxychains. In particular, traditional Nmap scanning features such as raw-packet SYN scans don't behave like normal TCP connections through a SOCKS proxy. SOCKS is most useful for applications/tools that make normal TCP connections.

---

# ProxyChains

**Goal:** Force command-line tools that do not natively support proxy configurations (e.g., `nmap`, `curl`, `telnet`, `impacket`) to route their traffic through one or multiple SOCKS/HTTP proxies.

Configure:   `sudo nano /etc/proxychains.conf `
```ini
[ProxyList]
socks4 127.0.0.1 1080
```

Run a command through it:
```bash
proxychains nxc smb 192.168.13.100 -u Administrator -H NTLM_HASH
```

Web:
```bash
proxychains curl http://192.168.13.71
```

### Nmap Through ProxyChains

Only **TCP connect scans** work:
```bash
proxychains nmap -sT -Pn TARGET
```

Important:
- `-sU` →  UDP doesn't work
- `-sS` →  SYN scan doesn't work
- `ping` / ICMP →  doesn't work
- `-sT` →  TCP connect scan work
- `-Pn` → skip host discovery
    
ProxyChains can also be **very slow**, so avoid using it unnecessarily.

---
#  The biggest thing to memorize

### Local forwarding

```bash
ssh -L LOCAL_PORT:TARGET_IP:TARGET_PORT user@PIVOT
```

You specify **one destination**.

```text
YOU → PIVOT → ONE TARGET
```

### Dynamic forwarding

```bash
ssh -D LOCAL_PORT user@PIVOT
```

You create a **SOCKS proxy**.

```text
YOU → SOCKS → PIVOT → MANY TARGETS
```

### Simple mental model

Think of `-L` as a **dedicated pipe**:

```text
        ┌──────────────→ DC:3389
YOU ────┤
        └── fixed destination
```

And `-D` as a **proxy gateway**:

```text
                  ┌→ DC:3389
                  ├→ DB:3306
YOU → SOCKS → PIVOT├→ Web:80
                  ├→ SSH:22
                  └→ SMB:445
```

