https://youtube.com/playlist?list=PLEx3X4axAW0TUBerU2T70-tWnapGKE6rp&si=FPy3C5j7YzXTgdDE

###  Already covered in my notes

|Topic|Status|
|---|---|
|AD Basics|✅|
|Kerberos authentication|✅|
|User enumeration|✅|
|Kerberos user enumeration / Kerbrute|✅|
|AS-REP Roasting|✅|
|SMB enumeration|✅|
|LDAP enumeration|✅|
|Domain SID enumeration|✅|
|SMB share/permission enumeration|✅|
|BloodHound / AD relationships|✅|
|Impacket basics|✅|
|DCSync|✅|
|NTDS.dit dumping|✅|
|Pass-the-Hash|✅|
|PsExec / Remote Service Execution|✅|
|Password cracking|✅|

###  Started / need deeper study

These appeared in my material, but I'd study them more:
- **Kerberoasting**
- **Password Spraying**
- **NTLM authentication**
- **Pass-the-Ticket**
- **Overpass-the-Hash**
- **Golden Ticket**
- **Silver Ticket**
- **Unconstrained Delegation**
- **Constrained Delegation**
- **RBCD**
- **AD Trusts**
- **AD Replication**
- **AD CS**
    

###  Still important to study

These are the biggest gaps I'd focus on next:

#### 1. ACL Abuse 
Learn:
```text
GenericAll
GenericWrite
WriteDACL
WriteOwner
ForceChangePassword
AddMember
```

Understand how they create privilege-escalation paths in BloodHound.

---

#### 2. NTLM Attacks 
Study:
```text
LLMNR poisoning
NBT-NS poisoning
Responder
SMB Relay
NTLM Relay
```

Especially understand:
```text
Victim
  ↓
NTLM authentication
  ↓
Attacker / Relay
  ↓
Target service
```

---

#### 3. Credential Dumping 

Study:
```text
LSASS
SAM
LSA Secrets
Windows Credential Manager
Cached Domain Credentials
```

Tools:
```text
Mimikatz
secretsdump.py
```

I have already used `secretsdump.py`, but now learn **what it's actually extracting and why**.

---

#### 4. GPO Abuse 

Learn how poorly configured Group Policy can lead to privilege escalation or code execution.

Important concepts:
```text
GPO
 ↓
Permissions
 ↓
Who can modify it?
 ↓
Which computers/users receive it?
```

---

#### 5. Delegation 

This should be a major focus because it's one of the more important AD attack areas.

Learn:
```text
Unconstrained Delegation
Constrained Delegation
RBCD
```

And understand:
```text
User → Service → Delegation → Privileged Account
```

---

#### 6. AD CS 

Don't stop at the basic AD CS concept.

Study:
```text
CA
Certificate Templates
Enrollment
EKUs
Misconfigured Templates
ESC1
ESC2
ESC3
ESC4
ESC8
```

AD CS can provide extremely powerful privilege-escalation paths.

---

#### 7. Lateral Movement 

Learn the different ways to move between machines:
```text
SMB / PsExec
WinRM
WMI
RDP
DCOM
Pass-the-Hash
Pass-the-Ticket
```

Understand **when each technique works and what privileges it requires**.

---

#### 8. Windows Privilege Escalation 

I know some Linux privilege escalation techniques, but I should add Windows:
```text
Services
Scheduled Tasks
Weak File Permissions
Unquoted Service Paths
Registry
AlwaysInstallElevated
Token Privileges
UAC
Stored Credentials
```

---

#### 9. DCShadow 

Less common than DCSync, but worth understanding after i finish AD replication.

Learn:
```text
DCSync
vs
DCShadow
```

The important distinction is:

> **DCSync reads/synchronizes directory data; DCShadow attempts to register a rogue DC and push changes into AD.**

---

#  Recommended order from here

I would **not** simply follow the playlist from beginning to end anymore. 

```text
                    YOU ARE HERE
                         │
                         ▼
              ┌────────────────────┐
              │ BloodHound + ACLs  │
              └─────────┬──────────┘
                        ↓
              ┌────────────────────┐
              │ NTLM Attacks       │
              │ Responder / Relay  │
              └─────────┬──────────┘
                        ↓
              ┌────────────────────┐
              │ Credential Dumping  │
              │ Mimikatz / LSASS   │
              └─────────┬──────────┘
                        ↓
              ┌────────────────────┐
              │ Lateral Movement   │
              └─────────┬──────────┘
                        ↓
              ┌────────────────────┐
              │ Kerberos Attacks   │
              │ Roast / Tickets    │
              └─────────┬──────────┘
                        ↓
              ┌────────────────────┐
              │ Delegation         │
              │ Unconstrained      │
              │ Constrained / RBCD  │
              └─────────┬──────────┘
                        ↓
              ┌────────────────────┐
              │ GPO Abuse          │
              └─────────┬──────────┘
                        ↓
              ┌────────────────────┐
              │ AD CS              │
              │ ESC techniques     │
              └─────────┬──────────┘
                        ↓
              ┌────────────────────┐
              │ Trusts / Replication│
              │ DCShadow            │
              └─────────┬──────────┘
                        ↓
              ┌────────────────────┐
              │ Windows PrivEsc    │
              └────────────────────┘
```

###  The **highest-priority remaining topics** are:
1. **ACL Abuse + BloodHound**
2. **Kerberoasting**
3. **Password Spraying**
4. **LLMNR/NBT-NS + Responder**
5. **SMB/NTLM Relay**
6. **Credential Dumping**
7. **Lateral Movement**
8. **Pass-the-Ticket / Overpass-the-Hash**
9. **Delegation: Unconstrained → Constrained → RBCD**
10. **GPO Abuse**
11. **AD CS / ESC attacks**
12. **AD Trusts**
13. **DCShadow**
14. **Windows Privilege Escalation**  


# Post-Exploitation Basics
https://tryhackme.com/room/postexploit

