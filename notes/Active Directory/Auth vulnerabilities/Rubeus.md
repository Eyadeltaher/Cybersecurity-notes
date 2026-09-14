## Overview

**Rubeus** is a C# tool from the GhostPack project used to interact with and attack **Kerberos** in Active Directory.

### Important capabilities
- Kerberos ticket harvesting.
- Overpass-the-Hash.
- Ticket requests and renewals.
- Ticket extraction and management.
- Pass-the-Ticket.
- AS-REP Roasting.
- Kerberoasting.
- Kerberos password spraying and brute-forcing.

> Rubeus is primarily a Windows tool and is commonly used during AD penetration testing after obtaining access to a domain-joined machine.


---

## 1. Ticket Harvesting

### What is ticket harvesting?

Ticket harvesting is the process of repeatedly looking for Kerberos tickets, especially **Ticket Granting Tickets (TGTs)**, that become available on a Windows machine.

A harvested TGT may be used to request service tickets from the KDC or perform other attacks, such as Pass-the-Ticket, depending on the ticket and the attacker's access.

### Command

```cmd
Rubeus.exe harvest /interval:30
```

### Explanation

| Part           | Meaning                                           |
| -------------- | ------------------------------------------------- |
| `Rubeus.exe`   | Execute Rubeus.                                   |
| `harvest`      | Start the ticket-harvesting function.             |
| `/interval:30` | Repeat the harvesting operation every 30 seconds. |

**Important:** The command continuously searches for relevant Kerberos tickets. Stop it with `Ctrl+C` when finished.

---

## 2. Kerberos Password Spraying

### What is password spraying?

Password spraying attempts **one password against many user accounts** instead of trying many passwords against one account.

This reduces the number of failed attempts per account, but it can still trigger domain account-lockout policies.

Rubeus can use Kerberos authentication to test a supplied password against discovered domain users. When valid credentials are found, it can obtain a TGT in `.kirbi` format.

### Prerequisite: Configure name resolution

Ensure the domain controller's IP address resolves to its domain name.

Edit the Windows hosts file:
```cmd
echo MACHINE_IP CONTROLLER.local >> C:\Windows\System32\drivers\etc\hosts
```
Replace `MACHINE_IP` with the domain controller's IP address.

Verify name resolution:
```cmd
ping CONTROLLER.local
```
> Administrative privileges may be required to modify the hosts file.

### Command

```cmd
Rubeus.exe brute /password:Password1 /noticket
```

### Explanation

| Part                  | Meaning                                                     |
| --------------------- | ----------------------------------------------------------- |
| `brute`               | Test a supplied password against domain users.              |
| `/password:Password1` | Specify the password to test.                               |
| `/noticket`           | Do not require an existing ticket to perform the operation. |

If valid credentials are found, Rubeus may obtain a **TGT** and save it as a `.kirbi` ticket file.

### How it works
1. Rubeus discovers domain usernames through Active Directory.
2. It attempts Kerberos authentication using `Password1` for those users.
3. If valid credentials are found, it can request and save a TGT as a `.kirbi` file.

### Important considerations
- Obtain authorization before performing password spraying.
- Check the domain's account-lockout policy.
- Use a controlled number of attempts.
- A successful authentication does not necessarily mean the account has administrative privileges.
- A TGT can be used to request service tickets from the KDC.
    
---

## 3. Kerberos Ticket Files

### `.kirbi` files

Rubeus commonly uses the `.kirbi` format to store Kerberos tickets.

A TGT can be used to request service tickets for services in the domain. Depending on the ticket and the user's privileges, tickets may also be used in Pass-the-Ticket attacks.

