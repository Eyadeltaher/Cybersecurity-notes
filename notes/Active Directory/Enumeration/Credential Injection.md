# 1. Why Windows instead of Kali?

You can do a lot of AD enumeration from Kali:

```text
Kali
 ├── Nmap
 ├── NetExec
 ├── Kerbrute
 ├── BloodHound
 ├── Impacket
 └── LDAP enumeration
```

But Windows has something Kali doesn't: **native Windows authentication mechanisms**.

For example:
```text
runas.exe
PowerShell
Windows SMB client
Windows authentication APIs
SQL Server Management Studio
Windows-integrated applications
```

So the idea is:
```text
              AD Network
                  │
                  │
          ┌───────▼───────┐
          │ Domain Control│
          │      ler      │
          └───────▲───────┘
                  │
             AD credentials
                  │
        ┌─────────┴─────────┐
        │ Your Windows PC   │
        │ NOT domain-joined │
        └───────────────────┘
```

You have the credentials, but your machine isn't part of the domain.

**`runas /netonly` bridges that gap.**

---

# 2. What problem does `runas /netonly` solve?

Imagine you discover:
```text
username: john
password: Password123!
domain: za.tryhackme.com
```

But your machine is:
```text
WORKGROUP
```

not:
```text
ZA
```

Normally, you can't simply log into Windows as:
```text
ZA\john
```

because your machine isn't domain-joined.

Instead:
```cmd
runas.exe /netonly /user:za.tryhackme.com\john cmd.exe
```

Windows creates a **new CMD process** associated with those supplied network credentials.

Think of it as:
```text
Your Windows account
        │
        │ starts
        ▼
┌──────────────────────────┐
│ New CMD                  │
│                          │
│ Local identity: YOU      │
│ Network credentials:     │
│ za.tryhackme.com\john    │
└────────────┬─────────────┘
             │
             │ network request
             ▼
       Active Directory
```

That's the important distinction.

---

# 3. `/netonly` is the key

This is probably the most important part of the entire section.

```cmd
runas.exe /netonly /user:domain\username cmd.exe
```

`/netonly` basically means:
> **Use these credentials only when authenticating to network resources.**

It does **not** change your local Windows identity.

For example, suppose you're logged into your computer as:
```text
EYAD-PC\eyad
```

and run:
```cmd
runas.exe /netonly /user:za.tryhackme.com\john cmd.exe
```

Inside the new CMD:

### Local operations
```cmd
whoami
```

will still show your local account:
```text
EYAD-PC\eyad
```

because `john` isn't your local Windows identity.

But when you access:
```text
\\za.tryhackme.com\SYSVOL
```

Windows can authenticate to the network using:
```text
za.tryhackme.com\john
```

So:
```text
LOCAL
  ↓
EYAD-PC\eyad

NETWORK
  ↓
za.tryhackme.com\john
```

That's why this technique is so useful.

---

# 4. Why does it ask for a password if it doesn't verify it?

This part is confusing at first.

You run:
```cmd
runas.exe /netonly /user:za.tryhackme.com\john cmd.exe
```

Windows asks:
```text
Enter the password for za.tryhackme.com\john:
```

You enter:
```text
Password123!
```

But `/netonly` means Windows doesn't immediately contact the Domain Controller and say:

> "Is this password correct?"

Instead, Windows stores the supplied credentials for **future network authentication**.

Therefore, even a wrong password can initially be accepted.

You only discover whether the credentials are actually valid when you try to access something that requires them.

For example:
```cmd
dir \\za.tryhackme.com\SYSVOL
```

If it succeeds:
```text
credentials + DNS + network authentication
```
are working.

---

# 5. Why do they recommend starting CMD as Administrator?

The tutorial says:
> Run your first Command Prompt as Administrator.

This is about your **local privileges**, not your AD privileges.

Suppose your local account is:
```text
EYAD-PC\eyad
```
and you are a local administrator.

You open an elevated CMD:
```text
Administrator CMD
       │
       ▼
runas /netonly ...
       │
       ▼
New CMD
```

The new process can have the appropriate local administrative token.

That means:
```text
Local machine
    → Administrator privileges

Network
    → AD account privileges
```

These are separate.

If `john` is just a normal domain user:
```text
Local Administrator
        ≠
Domain Administrator
```

`runas /netonly` does **not** magically make `john` a Domain Admin.

---

# 6. Why DNS matters

This is another major concept.

Active Directory relies heavily on DNS.

For example:
```text
za.tryhackme.com
        │
        ▼
    DC IP address
```

Your machine needs to know:
> "Which DNS server can tell me where `za.tryhackme.com` and its AD services are?"

In an AD environment, the **Domain Controller normally provides DNS**.

So they configure:
```powershell
$dnsip = "<DC IP>"

$index = Get-NetAdapter -Name 'Ethernet' |
    Select-Object -ExpandProperty 'ifIndex'

Set-DnsClientServerAddress `
    -InterfaceIndex $index `
    -ServerAddresses $dnsip
```

Then:
```cmd
nslookup za.tryhackme.com
```
should resolve correctly.

---

# 7. Why test with SYSVOL?

Now that you've injected credentials, you need to prove:
> **Can these credentials actually authenticate to the AD network?**

SYSVOL is a convenient test because domain users normally have read access to it.

You run:
```cmd
dir \\za.tryhackme.com\SYSVOL\
```

Notice that you're using:
```text
\\hostname\share
```
This is an SMB network request.

Therefore Windows has to authenticate to the remote machine.

If the command succeeds:
```text
runas credentials
        ↓
network authentication
        ↓
        DC
        ↓
       SMB
        ↓
      SYSVOL
```
You've confirmed that the credentials work.

---

# 8. Why is SYSVOL interesting for enumeration?

SYSVOL isn't just a random folder.

It contains domain-related files, especially:
```text
Group Policy Objects
Scripts
Configuration
Domain-related information
```

Historically, administrators have sometimes accidentally stored credentials or other sensitive information there.

So after gaining valid domain credentials, a pentester may enumerate SYSVOL looking for useful information.

Conceptually:
```text
SYSVOL
 ├── Group Policy
 ├── Scripts
 ├── Configuration
 └── Potentially exposed credentials/secrets
```

---

# 9. The IP vs hostname part is REALLY important

Compare:
```cmd
dir \\za.tryhackme.com\SYSVOL
```

with:
```cmd
dir \\10.10.10.10\SYSVOL
```

They look equivalent.

They're not necessarily equivalent from an authentication perspective.

### Hostname
```text
\\za.tryhackme.com\SYSVOL
```

can lead Windows toward:
```text
Kerberos
```

### IP address
```text
\\10.10.10.10\SYSVOL
```

typically cannot use Kerberos in the same way because Kerberos relies on service names/hostnames represented in the ticket.

This can result in:
```text
Hostname
   ↓
Kerberos
```

versus:
```text
IP address
   ↓
NTLM
```

---

#  The complete attack/assessment flow

The entire THM section can be reduced to this:

```text
1. Obtain AD credentials
        │
        ▼
username:password
        │
        ▼
2. You don't have a domain-joined machine
        │
        ▼
3. Use Windows
        │
        ▼
4. Configure AD DNS
        │
        ▼
5. Inject network credentials
        │
        │ runas /netonly
        ▼
6. New CMD process
        │
        ├── Local identity = your account
        │
        └── Network identity = AD account
        │
        ▼
7. Test authentication
        │
        │ dir \\domain\SYSVOL
        ▼
8. Confirm credentials work
        │
        ▼
9. Use applications/tools
   to interact with AD resources
```

---

**if the credentials give you RDP access, and you have a reachable RDP target, then using RDP is often simpler.** `runas /netonly` solves a different problem.

### Compare the situations

Suppose you find:
```text
DOMAIN\john : Password123!
```

#### Case 1 — You have an RDP target

If:
```text
THMJMP1
  └── RDP enabled
      └── john is allowed to RDP
```

Then you can simply:
```text
Kali → RDP → THMJMP1
             ↓
          john's session
```

### Case 2 — You DON'T have somewhere to log in

You have:
```text
Your Windows machine
        │
        │ NOT domain joined
        │
        └─────── AD network
```

You found:
```text
DOMAIN\john : password
```

But:
- You don't have RDP access to a machine.
- You don't have permission to create a domain-joined machine.
- You don't want/need an interactive desktop session.
- You want to use Windows-native tools from **your own machine**.

That's where:
```cmd
runas.exe /netonly /user:DOMAIN\john cmd.exe
```

becomes useful.

---

### The big difference

**RDP:**
> "Give me an interactive Windows session on another machine as John."

**`runas /netonly`:**
> "Keep me on my current machine, but use John's credentials when this process accesses network resources."

Think:
```text
RDP
────────────────────────────

Your PC
   │
   │ RDP
   ▼
┌─────────────────┐
│ Domain machine  │
│                 │
│ Logged in John  │
└─────────────────┘
```

versus:
```text
runas /netonly
────────────────────────────

Your PC
   │
   ▼
┌──────────────────────────────┐
│ Your Windows machine         │
│                              │
│ Local: Eyad                  │
│ Network: DOMAIN\John         │
│                              │
│ ┌──────────────┐             │
│ │ CMD/Tools    │─────────────┼──→ AD resources
│ └──────────────┘             │
└──────────────────────────────┘
```

