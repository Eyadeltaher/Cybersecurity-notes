The **Metasploit Framework** is the most widely used open-source exploitation framework in the penetration testing industry.
### Metasploit supports the full penetration testing lifecycle:
- **Information gathering**: Scanning targets and fingerprinting services
- **Vulnerability identification**: Detecting known flaws in target systems
- **Exploitation**: Delivering exploit code to take advantage of those flaws
- **Post-exploitation**: Maintaining access, gathering data, and pivoting to other systems
- **Reporting**: Logging findings for documentation and client deliverables

---

## The Three Pillars of the Framework

**1. Msfconsole**
`msfconsole` is the primary command-line interface for the Metasploit Framework. you can search for modules, configure parameters, launch exploits, and manage sessions on compromised targets.

**2. Modules**
Modules are the building blocks of Metasploit. Each module is a self-contained piece of code designed to perform a specific task. There are seven categories of modules (exploits, auxiliary, payloads, post-exploitation, encoders, NOPs, and evasion).

**3. Tools**
the framework ships with a set of standalone command-line tools. The most important one for this module is `msfvenom`, which generates payloads outside of `msfconsole` for use in scenarios where you need a standalone file (an executable, a web shell, or raw shellcode).

---
## The Seven Module Categories
Metasploit organizes its entire library into seven categories of modules. Each category serves a distinct role in the penetration testing workflow.

**Exploits**
Exploit modules target a specific vulnerability on a specific platform.

**Auxiliary**
Auxiliary modules handle everything that is _not_ direct exploitation. This includes port scanners, service fingerprinters, brute-force login modules, fuzzers, and network sniffers.

**Payloads**
Payload modules contain the code that executes on the target after a successful exploit. 

**Post-Exploitation**
Post modules run _after_ you have already gained access to a target through an active session. They automate common post-exploitation tasks: dumping password hashes, enumerating system information, capturing screenshots, pivoting to other network segments, and more.

**Encoders**
Encoder modules transform payload data into a different format. The most well-known encoder is `x86/shikata_ga_nai`, which applies polymorphic XOR encoding. It is _not_ a reliable antivirus evasion technique on its own. Modern endpoint detection solutions look far beyond simple signature matching. 

**NOPs**
You will rarely interact with NOP modules directly; Metasploit handles NOP sled generation automatically when needed.

**Evasion**
Evasion modules are purpose-built attempts to bypass specific security controls, such as Windows Defender or AppLockerd.

---
## Payload Types: Singles, Stagers, and Stages

Within the payload category, Metasploit distinguishes between three types.

**Singles** are self-contained. The entire payload is delivered in a single package. A single payload might add a user account, execute a system command, or open a bind shell. Because everything is in one piece, singles tend to be larger but more reliable; there is no second download that could fail or be blocked.

**Stagers** are small, lightweight payloads whose only job is to establish a communication channel between the attacker and the target. Once connected, the stager downloads the second component.

**Stages** are the larger payload components downloaded by a stager. Together, a stager and its stage form a **staged payload**. The advantage is a smaller initial footprint; the disadvantage is that the connection must remain stable long enough for the stage to download.

---
## Reading the Naming Convention

- `windows/x64/shell_reverse_tcp` — The underscore (`_`) between `shell` and `reverse` means this is a **single** (stageless) payload. Everything is in one package.

- `windows/x64/shell/reverse_tcp` — The forward slash (`/`) between `shell` and `reverse` means this is a **staged** payload. A small stager connects first, then downloads the full shell stage.

This naming pattern is consistent across the entire framework. Once you recognize it, you can identify any payload's type at a glance.

The general structure of a payload path is:
`<platform>/<architecture>/<payload_type><separator><connection_method>`

---
## Running Linux Commands Inside Msfconsole
* One of the convenient features of `msfconsole` is that it supports most standard commands. You do not need to exit the console to check an IP address, read a file, or list directory contents
* `msfconsole` does not support all shell features. Output redirection, for example, does not work:

## Getting Help
The `help` command displays the full list of available `msfconsole` commands. You can also use it with a specific command name to see that command's usage:
```shell-session
msf6 > help search
```

* Use the `history` command to see your recent inputs

---
## Searching for Modules
The simplest form is `search` followed by a keyword. Metasploit will return every module whose name, description, or references match that keyword:

**#**: A numeric index. You can use this number with commands like `use` or `info` (e.g., `use 0` or `info 0`) instead of typing the full module path.

**Filtered search**
The most useful filters for day-to-day work are:
- `type`: Filter by module category (`exploit`, `auxiliary`, `post`, `payload`, `encoder`, `nop`, `evasion`)
- `platform`: Filter by target OS (`windows`, `linux`, `osx`, `android`, etc.)
- `cve`: Search by identifier
- `name`: Match against the module's descriptive name only

Example
```shell-session
msf6 > search type:auxiliary name:smb
```

---
### Understanding Exploit Rankings
The **Rank** column in search results tells you how reliable an exploit is expected to be

|Rank|Meaning|
|---|---|
|**Excellent**|The exploit will never crash the service. Typically, SQL injection, command execution, or file inclusion vulnerabilities are inherently safe to exploit.|
|**Great**|The exploit has a default target that auto-detects the correct configuration (e.g., return address), making it reliable across common setups.|
|**Good**|The exploit has a default target that covers the most common case, but does not auto-detect.|
|**Normal**|The exploit works reliably against a specific version of the target but does not auto-detect or have a broadly applicable default.|
|**Average**|The exploit is generally unreliable but has a success rate above 50%.|
|**Low**|The exploit succeeds less than 50% of the time.|
|**Manual**|The exploit is essentially a denial-of-service or requires significant manual configuration. Success rate is 15% or lower.|

---
## Inspecting a Module with Info

Once you have found a promising module, the `info` command gives you detailed information about it. You can use `info` in two ways:
1. Directly from the `msf6 >` prompt with the module path: `info exploit/windows/smb/ms17_010_eternalblue`
2. Using the numeric index from search results: `info 0`

Pay attention to a few key fields:
- **Privileged**: If `Yes`, a successful exploit will give you elevated (SYSTEM/root) privileges on the target. If `No`, you land with the privileges of the exploited service.
- **Check supported**: If `Yes`, you can verify whether the target is vulnerable _without_ sending the exploit payload. This is safer in production environments where crashing a service is unacceptable.
- **Available targets**: Some modules support multiple target configurations. The default is usually sufficient, but in some cases you may need to select a specific target (e.g., a particular Windows service pack or application version).

---
# Dealing with Modules

The `use` command loads a module into your current context
```bash
msf6 > use exploit/windows/smb/ms17_010_eternalblue
[*] No payload configured, defaulting to windows/x64/meterpreter/reverse_tcp
msf6 exploit(windows/smb/ms17_010_eternalblue) >
```

**An important detail:** loading a module does not change your working directory. You are not "inside" a folder. You are still at the same `msfconsole` session; the context simply tells Metasploit which module's options and commands to apply. You can confirm this by running any Linux command (like `whoami`) from within a module context and seeing that it still works.

To leave a module context and return to the bare `msf6 >` prompt, use the `back` command:

## Reading Show Options
Once a module is loaded, `show options` displays every configurable parameter

**Module options** are parameters specific to the exploit itself. These control _where_ and _how_ the exploit connects to the target. `RHOSTS` (the target IP) is blank and marked `Required: yes`, which means the exploit will refuse to run until we provide a value. 

**Payload options** are parameters for the selected payload. `LHOST` (your attacking machine's IP) and `LPORT` (the port your machine will listen on for the reverse connection) are the two you will set most frequently. Metasploit often auto-detects `LHOST` from your active network interfaces, but you should always verify it is correct, especially when working through a VPN tunnel.

**Exploit target** specifies which version or configuration of the target software the exploit is tuned for. Many modern modules use `Automatic Target`, which auto-detects the right configuration. Older modules may require you to manually select a target (e.g., a specific Windows service pack) using `set TARGET <id>`.

The **Required** column is your checklist. Every parameter marked `yes` must have a value before the module will run. Parameters marked `no` are optional and can be left blank.

## The Core Parameters

While every module has its own set of options, six parameters appear so frequently that you should know them by name:

- **RHOSTS**: "Remote host(s)." The target's IP address. Accepts a single IP (`10.112.184.63`), a CIDR range (`10.112.184.63/24`), a hyphenated range (`10.48.12.1-10.48.12.50`), or a file containing one target per line (`file:/path/to/targets.txt`).
- **RPORT**: "Remote port." The port on the target where the vulnerable service is running. Usually pre-populated with the service's default port.
- **LHOST**: "Local host." Your attacking machine's IP address. This is where the target will connect back to for reverse payloads.
- **LPORT**: "Local port." The port on your machine that will receive the reverse connection. Default is `4444`. You can change this to any unused port.
- **PAYLOAD**: The payload to deliver with the exploit. A default is usually pre-selected, but you can override it.
- **SESSION**: Used with post-exploitation modules. Specifies which existing session to run the module through. We will cover sessions in the next task.

## Setting Parameters

The `set` command assigns a value to a parameter within the current module context:
```shell-session
set RHOSTS 10.112.184.63
set LPORT 5555
```

To clear a single parameter, use `unset`: `unset RHOSTS`

### Local vs. Global: Set vs. Setg

Parameters set with `set` are **local** to the current module. If you switch to a different module (using `use` or `back` followed by another `use`), those values are gone. You would need to set them again.

The `setg` command sets a **global** value that persists across all modules for the duration of your `msfconsole` session. This is useful when you are working against the same target with multiple modules.


## Selecting a Different Payload

Metasploit automatically assigns a default payload when you load an exploit. To see all compatible payloads for the current module, use `show payloads`:

Only payloads that are compatible with the exploit's target architecture and platform are shown. To switch payloads, use `set PAYLOAD` followed by the payload name or index number:
```shell-session
set PAYLOAD windows/x64/shell/reverse_tcp
set PAYLOAD 3
```

## Running the Module
Once all required parameters are set, you launch the module with `exploit` (or its alias `run`)

**The `run` alias**: most pentesters use `run` for auxiliary modules and `exploit` for exploit modules, but either works in any context.

**The `-z` flag**: Adding `-z` to the `exploit` command runs the exploit and immediately backgrounds the session once it opens, returning you to the module context prompt instead of dropping you into the Meterpreter session:

## Checking Before Exploiting
Some modules support the `check` command, which probes the target to determine if it is vulnerable _without_ sending the exploit payload.

Not all modules support `check` (recall the **Check** column in search results). When it is available, running `check` before `exploit` is good practice, especially in production environments where a failed exploit could crash a service or trigger alerts.


## What Is a Session?
A **session** in Metasploit is an active communication channel between your attacking machine and a compromised target.

Sessions can be different types depending on the payload that created them:
- **Meterpreter sessions** provide a rich, interactive environment with built-in commands for file system access, privilege escalation, pivoting, and more. These are the most common and most capable session types.
- **Shell sessions** provide a basic operating system command line (e.g., `cmd.exe` on Windows, `/bin/sh` on Linux). These are simpler but less feature-rich.
- **Protocol-specific sessions** (newer in Metasploit 6.4) provide interactive access to services like SMB, MSSQL, MySQL, and PostgreSQL. These are specialized and used for targeted enumeration rather than general access.

## Backgrounding a Session
When you are in an active session (you see `meterpreter >` or a shell prompt from the target), you can return to the `msfconsole` prompt without closing the session. This is called **backgrounding**.
Use the `background` command (or its shortcut, `CTRL+Z`).

## Listing Active Sessions
The `sessions` command (with no arguments) displays all active sessions.

- **Id**: The session's unique numeric identifier. You will use this number to interact with, kill, or route traffic through a specific session.
- **Name**: An optional label you can assign with `sessions -n <name> -i <id>`. Useful for keeping track of which session is which during complex engagements.
- **Type**: The session type and architecture (e.g., `meterpreter x64/windows`, `shell x64/linux`).
- **Information**: For Meterpreter sessions, this shows the user context and hostname. This tells you at a glance whether you landed as `NT AUTHORITY\SYSTEM` (full privileges) or as a regular user. Shell sessions may leave this column blank.
- **Connection**: The local and remote IP:port pair, showing exactly which machine and port each session is connected through.

## Interacting with a Session
To switch to a different session, background the current one first (`background` or `CTRL+Z`), then interact with the other

To switch to a specific session, use `sessions -i` followed by the session ID
example --> `sessions -i 1`

## Closing Sessions
To terminate a specific session, use `sessions -k` followed by the session ID
example --> `sessions -k 1`

To kill _all_ active sessions at once --> `sessions -K`

## Sessions and Post-Exploitation Modules

Sessions are not just interactive terminals; they are also the bridge to Metasploit's post-exploitation modules. Many `post/` modules require a `SESSION` parameter that points to an existing session.

The workflow looks like this:
1. Exploit a target and open a Meterpreter session
2. Background the session
3. Load a post-exploitation module with `use`
4. Set the `SESSION` parameter to the relevant session ID
5. Run the module

---
# Quick Cheat Sheet

```bash
# Start
msfconsole

# Help
help
help search
history

# Search
search smb
search type:auxiliary name:smb
search cve:<CVE>

# Information
info 0
info <module_path>

# Load
use <module>

# Leave module
back

# Options
show options

# Payloads
show payloads
set PAYLOAD <payload>

# Configure
set RHOSTS <target>
set RPORT <port>
set LHOST <your-ip>
set LPORT <port>
set SESSION <id>

# Global configuration
setg RHOSTS <target>

# Remove setting
unset RHOSTS

# Test
check

# Execute
run
exploit
exploit -z

# Sessions
sessions
sessions -i 1
sessions -k 1
sessions -K

# Meterpreter
sysinfo
getuid
hashdump
shell
background
```

### The main workflow to memorize

```text
msfconsole
    ↓
  search
    ↓
   use
    ↓
   info
    ↓
show options
    ↓
set RHOSTS / RPORT / LHOST / LPORT
    ↓
set PAYLOAD
    ↓
  check
    ↓
 exploit
    ↓
 sessions
    ↓
sessions -i <ID>
    ↓
background
    ↓
 use post/...
    ↓
set SESSION <ID>
    ↓
   run
```