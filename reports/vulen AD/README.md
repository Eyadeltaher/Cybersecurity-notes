# Active Directory Penetration Testing — `cs.org`

A hands-on **Active Directory penetration testing assessment** performed against a deliberately vulnerable Windows Server 2022 domain environment as part of a DEPI cybersecurity training lab.

The assessment demonstrates a complete attack chain starting from unauthenticated reconnaissance and username enumeration, progressing through credential attacks and Kerberos abuse, and ultimately achieving **Domain Administrator compromise and persistence**.

> **Disclaimer:** This repository contains material from an isolated, intentionally vulnerable training environment. The techniques and commands documented here are intended strictly for authorized labs, CTFs, and security assessments.

---

##  Project Overview

| Item                  | Details                                                  |
| --------------------- | -------------------------------------------------------- |
| **Assessment Type**   | Gray-box Internal Penetration Test                       |
| **Environment**       | Vulnerable Active Directory Lab                          |
| **Domain**            | `cs.org`                                                 |
| **Domain Controller** | `DC01`                                                   |
| **Operating System**  | Windows Server 2022                                      |
| **Target IP**         | `192.168.56.10`                                          |
| **Assessment Period** | 27–29 September 2026                                     |
| **Primary Goal**      | Identify and demonstrate AD attack paths to Domain Admin |
| **Result**            | Domain compromise achieved                               |

The engagement began without domain credentials and resulted in full domain compromise through multiple independent attack paths.

---

##  Objectives

The assessment focused on:

* Active Directory reconnaissance and enumeration
* Kerberos username enumeration
* Password spraying
* SMB and LDAP enumeration
* BloodHound attack-path analysis
* AS-REP Roasting
* Kerberoasting
* Credential discovery and offline password cracking
* NTLMv2 credential capture
* DCSync
* Golden Ticket attacks
* Silver Ticket attacks
* Remote Code Execution through WMI
* Scheduled-task persistence
* Domain account creation
* Privileged group DACL manipulation
* Windows Security Event Log analysis
* Security remediation recommendations

---

##  Lab Environment

```text
                    ┌─────────────────────────┐
                    │       Attacker          │
                    │      Linux / Kali       │
                    │                         │
                    │   Kerbrute / NetExec    │
                    │  BloodHound / Impacket  │
                    │   Responder / Hashcat   │
                    └────────────┬────────────┘
                                 │
                         192.168.56.0/24
                                 │
                                 ▼
                    ┌──────────────────────────┐
                    │          DC01            │
                    │   Windows Server 2022    │
                    │                          │
                    │     Domain: cs.org       │
                    │    IP: 192.168.56.10     │
                    │                          │
                    │    AD DS + DNS + LDAP    │
                    │  Kerberos + SMB + WinRM  │
                    └──────────────────────────┘
```

The domain contained **107 users, 60 groups, 2 GPOs, 1 OU, and a single Domain Controller**, with no domain trusts identified.

---

#  Attack Chain

The assessment demonstrated the following progression:

```text
  Unauthenticated Reconnaissance
            │
            ▼
   Kerberos Username Enumeration
            │
            ▼
       Password Spraying
            │
            ▼
    Low-Privilege Foothold
            │
      ┌─────┴──────────────┐
      ▼                    ▼
 AS-REP Roasting     AD Enumeration
      │                   │
      ▼                   ▼
 Credential          Kerberoasting
  Cracking                │
      │                   ▼
      └──────────►  Service Account
                      Compromise
                          │
                          ▼
                 SMB Share Enumeration
                          │
                          ▼
                 Writable Share Abuse
                          │
                          ▼
                  Responder / NTLMv2
                          │
                          ▼
                  Domain Administrator
                          │
                          ▼
                       DCSync
                          │
              ┌───────────┴───────────┐
              ▼                       ▼
        Golden Ticket           Silver Ticket
              │                       │
              └───────────┬───────────┘
                          ▼
                   Domain Persistence
                          │
              ┌───────────┴───────────┐
              ▼                       ▼
        Scheduled Task          DACL Abuse
                                      │
                                      ▼
                              Persistent Privilege
```

Multiple independent paths to privileged access were identified during the assessment.

---

#  Attack Paths

## 1. Username Enumeration → Password Spraying

**Severity:** High

Kerberos username enumeration was used to identify valid domain accounts. A password spray against the discovered accounts subsequently produced the initial domain foothold.

**Tools:**

* Kerbrute
* NetExec

**MITRE ATT&CK:**

* `T1589.001` — Gather Victim Identity Information
* `T1110.003` — Password Spraying

**Result:**

* 102 valid usernames identified
* Low-privilege domain access obtained
* Further SMB/LDAP enumeration became possible

The domain did not have an account lockout threshold configured, allowing password spraying without triggering lockout.

---

## 2. AS-REP Roasting

**Severity:** High

An account configured with `DONT_REQUIRE_PREAUTH` was identified and targeted for AS-REP Roasting.

**Tools:**

* Impacket `GetNPUsers.py`
* Hashcat

**MITRE ATT&CK:**

* `T1558.004` — Steal or Forge Kerberos Tickets: AS-REP Roasting

The captured AS-REP material was cracked offline, resulting in valid domain credentials.

---

## 3. Plaintext Passwords in AD Descriptions

**Severity:** Medium

Sensitive credential information was discovered inside Active Directory user description fields.

This demonstrated how seemingly harmless directory metadata can expose credentials to authenticated domain users.

**Tools:**

* NetExec
* LDAP enumeration
* `ldapdomaindump`

**Impact:**

* Credentials exposed through directory enumeration
* Additional valid accounts discovered
* Potential lateral movement

---

## 4. Kerberoasting

**Severity:** High

Multiple service accounts were configured with Service Principal Names (SPNs), making them candidates for Kerberoasting.

**Identified service accounts:**

```text
http_svc$
mssql_svc$
exchange_svc$
```

**Tools:**

* NetExec
* BloodHound
* Hashcat

**MITRE ATT&CK:**

* `T1558.003` — Steal or Forge Kerberos Tickets: Kerberoasting

TGS hashes were obtained and subjected to offline password cracking.

---

## 5. NTLMv2 Credential Capture

**Severity:** High

A writable SMB share was identified and abused to trigger NTLM authentication toward an attacker-controlled Responder listener.

**Tools:**

* `smbclient`
* Responder
* Hashcat

**MITRE ATT&CK:**

* `T1557.001` — Adversary-in-the-Middle: LLMNR/NBT-NS Poisoning

The resulting NTLMv2 credential material was successfully cracked, leading to Domain Administrator access in the lab.

The attack was enabled by a combination of:

```text
Writable SMB Share
        +
NTLM Authentication
        +
Name Resolution Poisoning
        ↓
NTLMv2 Credential Capture
```

---

#  Domain Compromise

## DCSync

After obtaining privileged credentials, DCSync was performed using the directory replication mechanism.

**Tool:**

* Impacket `secretsdump.py`

**MITRE ATT&CK:**

* `T1003.006` — OS Credential Dumping: DCSync

The operation resulted in extraction of domain credential material, including privileged accounts and Kerberos-related secrets.

---

## Golden Ticket

The domain `krbtgt` secret obtained during credential dumping was used in the lab to demonstrate Golden Ticket creation.

**Tool:**

* Impacket `ticketer.py`

**MITRE ATT&CK:**

* `T1558.001` — Golden Ticket

The forged ticket was then used to authenticate against the domain as a privileged identity.

---

## Silver Ticket

The Domain Controller machine-account secret was used to demonstrate a service-specific Silver Ticket targeting CIFS.

**MITRE ATT&CK:**

* `T1558.002` — Silver Ticket

This demonstrated the difference between domain-wide Golden Ticket abuse and service-specific Silver Ticket abuse.

---

#  Persistence

Two persistence mechanisms were demonstrated after obtaining privileged access.

### Scheduled Task

A scheduled task configured to execute as `SYSTEM` was created and triggered at logon.

**MITRE ATT&CK:**

* `T1053.005` — Scheduled Task/Job: Scheduled Task

The task creation generated:

```text
Event ID: 4698
```

### Domain User + DACL Abuse

A new domain account was created and granted `FullControl` over the **Domain Admins** group through DACL modification.

**MITRE ATT&CK:**

* `T1098` — Account Manipulation
* `T1222.001` — File and Directory Permissions Modification

Relevant Windows events included:

```text
4720 — User account created
5136 — Directory Service object modified
```

---

#  MITRE ATT&CK Coverage

| Technique                             | ID          |
| ------------------------------------- | ----------- | 
| Gather Victim Identity Information    | `T1589.001` | 
| Password Spraying                     | `T1110.003` | 
| AS-REP Roasting                       | `T1558.004` | 
| Kerberoasting                         | `T1558.003` | 
| Adversary-in-the-Middle: LLMNR/NBT-NS | `T1557.001` | 
| DCSync                                | `T1003.006` |
| Golden Ticket                         | `T1558.001` | 
| Silver Ticket                         | `T1558.002` | 
| Scheduled Task                        | `T1053.005` | 
| Account Manipulation                  | `T1098`     | 
| DACL Modification                     | `T1222.001` | 

---

#  Tools Used

### Reconnaissance & Enumeration

* Nmap
* Kerbrute
* NetExec
* LDAP
* `ldapdomaindump`
* BloodHound Community Edition
* SMB enumeration

### Credential Attacks

* Hashcat
* Impacket
* GetNPUsers
* Kerberoasting
* Responder

### Post-Exploitation

* `secretsdump.py`
* `ticketer.py`
* `wmiexec.py`
* NetExec

### Persistence & AD Manipulation

* bloodyAD
* `dacledit.py`
* Windows `schtasks`

---

#  Key Findings

| Severity  | Finding                         | Impact                                   |
| --------- | ------------------------------- | ---------------------------------------- |
|  High   | No account lockout threshold    | Password spraying / brute-force exposure |
|  High   | AS-REP Roastable account        | Offline credential cracking              |
|  High   | Kerberoastable service accounts | Service account compromise               |
|  High   | NTLM credential capture path    | Domain Administrator compromise          |
|  High   | Excessive DCSync capability     | Domain-wide credential extraction        |
|  Medium | Passwords in AD descriptions    | Credential exposure                      |
|  Medium | Writable SMB share              | Credential capture attack path           |
|  Medium | Weak password policy            | Credential attack exposure               |
|  Medium | Privileged DACL abuse           | Persistent administrative access         |

The report identified particularly weak password controls: a **4-character minimum password length, disabled complexity, and no account lockout threshold**.

---

#  Remediation Highlights

The assessment recommended:

* Rotate the `krbtgt` password twice after Golden Ticket compromise.
* Reset compromised privileged and domain credentials.
* Enforce SMB signing.
* Disable LLMNR and NBT-NS where appropriate.
* Implement account lockout / smart lockout controls.
* Remove `DONT_REQUIRE_PREAUTH` where unnecessary.
* Migrate service accounts to **gMSA** where possible.
* Remove passwords and sensitive information from AD descriptions.
* Restrict DCSync permissions.
* Audit privileged-group ACLs.
* Monitor scheduled-task creation.
* Monitor account creation and directory-service modifications.
* Implement stronger password policies.
* Restrict write access to SMB shares.

The report's remediation plan prioritizes credential compromise, `krbtgt` exposure, attacker-created persistence, SMB signing, password spraying, and Kerberos weaknesses.


---

#  Full Report

The complete penetration testing report contains:

* Executive Summary
* Scope & Target Information
* Network and AD Enumeration
* BloodHound Attack Paths
* Detailed Vulnerability Findings
* Exploitation Evidence
* Credential Attack Analysis
* DCSync / Golden Ticket / Silver Ticket
* Persistence Techniques
* Windows Event Log Analysis
* Password Policy Assessment
* Remediation Plan
* Tool and Command Reference


---

#  Learning Outcomes

This project provided practical experience with:

* Active Directory reconnaissance
* Kerberos authentication attacks
* Windows domain enumeration
* Credential discovery
* Offline password cracking
* SMB security
* NTLM authentication
* BloodHound attack-path analysis
* Active Directory privilege escalation
* Domain credential dumping
* Kerberos ticket forgery
* Windows persistence mechanisms
* AD ACL/DACL abuse
* Windows Security Event Log analysis
* Security remediation

---

#  Ethical Use

All techniques demonstrated in this repository were performed against an **isolated, intentionally vulnerable training environment**.

Do not use these techniques against systems, networks, accounts, or organizations without explicit authorization.

The purpose of this project is to demonstrate practical penetration-testing methodology and improve defensive understanding of Active Directory attack paths.

---

##  Author

**Eyad Islam Mohammed Eltaher**

 Web & Active Directory Penetration Tester



