
**Lateral Movement** is the process of moving from a compromised host to other systems in a network using stolen credentials, hashes, or Kerberos tickets.

**Core loop:**
`Compromise Host → Harvest Credentials → Authenticate to Another Host → Repeat`

### Main Techniques

#### 1. Remote Execution
Execute commands on another Windows host using legitimate administration protocols.

Common methods:
- **PsExec** → SMB + Windows Service
- **WMIExec** → WMI
- **SMBExec** → SMB
- **DCOMExec** → DCOM
- **WinRM** → Remote PowerShell
- **ATExec** → Scheduled Tasks

Tools:
```bash
impacket-psexec
impacket-wmiexec
impacket-smbexec
impacket-dcomexec
evil-winrm
NetExec (nxc)
```

#### 2. Credential Reuse

Use recovered authentication material to access other hosts.
- **Pass-the-Hash (PtH)** → authenticate using an NTLM hash without knowing the password.
- **Pass-the-Ticket (PtT)** → authenticate using a stolen Kerberos ticket.
- **Overpass-the-Hash** → use an NTLM hash to obtain a Kerberos ticket.
    

> Local Administrator ≠ Domain Administrator. However, a local admin account may provide access to credentials belonging to privileged domain users.

### Requirements

Usually you need:

1. **Authentication material**
    - Plaintext password
    - NTLM hash
    - Kerberos ticket
        
2. **Required privileges on the target**
    - Many remote execution methods require **Local Administrator**
    - WinRM can also work with appropriate **Remote Management Users** permissions.
        

---

# Pivoting

**Pivoting** is using a compromised host as a bridge to reach systems/networks that are not directly accessible from the attacker machine.

```text
Attacker
   |
   v
Compromised Host
   |
   +----> Internal Host 1
   +----> Internal Host 2
   +----> Domain Controller
```

### Two Main Pivoting Methods

#### Tunnelling / Proxying

Routes traffic through a compromised host into an internal network.

Useful for:
- Scanning internal networks
- Accessing multiple hosts/ports
- Tools such as Nmap
    

Common tools:
```text
Proxychains
FoxyProxy
Chisel
sshuttle
Ligolo-ng
```

#### Port Forwarding

Forwards a local port through a compromised host to a specific target/port.
```text
Attacker:13389
     |
     v
Pivot Host
     |
     v
Internal:3389
```

Example:
```bash
ssh -L 13389:192.168.13.100:3389 user@pivot
```

Then connect to:
```bash
xfreerdp /v:127.0.0.1:13389
```

**Port forwarding:** specific port(s), simple and reliable.
**Proxy/tunnel:** broader access to multiple hosts and ports.

### Common Pivoting Tools

|Tool|Purpose|
|---|---|
|`ssh`|SSH tunnelling / port forwarding|
|`sshuttle`|Route network traffic through SSH|
|`proxychains`|Send applications through SOCKS proxy|
|`chisel`|TCP tunnelling / SOCKS proxy|
|`ligolo-ng`|Advanced tunnelling|
|`socat`|Port forwarding / relaying|
|`plink.exe`|SSH tunnelling from Windows|

### Practical Workflow
```text
1. Compromise host
2. Enumerate network interfaces/routes
3. Identify reachable internal hosts
4. Find credentials/hashes/tickets
5. Test lateral movement
6. Pivot if target network is inaccessible
7. Repeat until reaching the objective
```

**Key idea:** Lateral movement gets you from **host → host**; pivoting gets you from **network → network** through a compromised host.