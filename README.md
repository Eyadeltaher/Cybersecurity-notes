# Cybersecurity Notes

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](./LICENSE)
[![Last Commit](https://img.shields.io/github/last-commit/Eyadeltaher/Cybersecurity-notes)](https://github.com/Eyadeltaher/Cybersecurity-notes/commits/main)

A personal **cybersecurity knowledge base** containing notes, methodologies, checklists, tools, payloads, scripts, CTF write-ups, and practical penetration testing reports.

This repository documents my learning journey across **Web Application Security, Active Directory, Privilege Escalation, Network Security, Reconnaissance, Exploitation, and CTFs**.

The notes are built through hands-on labs, practical exercises, security research, and platforms such as **PortSwigger Web Security Academy, TryHackMe, and vulnerable machines**.

---

# Repository Structure

```text
.
├── notes/
│   ├── Active Directory/
│   ├── API Penetration Testing/
│   ├── CTFs & Write-Ups/
│   ├── Metasploit & Nmap/
│   ├── Privilege Escalation/
│   ├── Protocols/
│   └── Web Security/
│
├── reports/
│   ├── Attacktive Directory (AD)/
│   └── metasploitable2/
│
├── LICENSE
└── README.md
```

---

# Notes

## Active Directory

Notes covering Active Directory penetration testing and common attack techniques.

Topics currently include:

* Active Directory Fundamentals
* AD Authentication
* Domain Enumeration
* LDAP Enumeration
* SMB Enumeration
* User Enumeration
* BloodHound
* AS-REP Roasting
* Kerberoasting
* Password Spraying
* NTLM Hash Cracking
* Pass-the-Hash
* Authentication Coercion
* DCSync
* Golden Ticket
* Remote Code Execution

```text
notes/Active Directory/
├── AD Basics.md
├── Auth vulnerabilities/
└── Enumeration/
```

---

## Web Security

Web application penetration testing notes organized by attack category.

### Authentication

* Authentication
* JWT
* OAuth 2.0

### Client-Side

* Cross-Site Scripting (XSS)
* Cross-Site Request Forgery (CSRF)
* Clickjacking

### File Handling

* File Upload
* Path Traversal
* LFI / LFD / RFI

### Injection

* SQL Injection
* NoSQL Injection
* OS Command Injection
* Server-Side Template Injection (SSTI)
* XML External Entity (XXE)

### Server-Side

* Access Control
* Business Logic
* CORS
* HTTP Host Header Attacks
* Information Disclosure
* Insecure Deserialization
* Open Redirect
* Race Conditions
* Server-Side Request Forgery (SSRF)

Most topics contain a combination of:

* Testing methodology
* Checklists
* Payloads
* Practical examples
* Exploitation techniques
* Burp Suite techniques
* Scripts and automation
* Mitigation notes

---

## API Penetration Testing

Notes focused on API security testing, including:

* API Security Fundamentals
* API testing concepts
* API attack surface
* API-specific testing techniques

---

## Reconnaissance

Resources and notes for the reconnaissance phase of penetration testing.

Includes:

* Passive Reconnaissance
* Active Reconnaissance
* Web Application Reconnaissance
* Directory Enumeration
* Google Dorks
* Bug Bounty Dorks
* SecretFinder
* icoHash
* Recon Methodology
* Recon Checklists

---

## Privilege Escalation

Privilege escalation techniques for both Linux and Windows environments.

### Linux

* Linux Permissions
* SUID
* Capabilities
* Cron Jobs
* NFS
* Kernel Exploits
* Environment Variables
* Service Exploitation
* AppArmor
* LinPEAS
* GTFOBins
* `/tmp` vs `/dev/shm`

### Windows

* Windows Fundamentals
* Windows Privilege Escalation

---

## Metasploit & Nmap

Practical notes for common exploitation and network scanning tools.

### Metasploit

* Metasploit Fundamentals
* Scanning & Exploitation
* Shells & Listeners
* Payload Generation & Delivery
* Post-Exploitation

### Nmap

* Network Scanning
* Service Enumeration
* NSE Scripts
* Practical scanning techniques

---

## Protocols

Notes covering protocols and services commonly encountered during penetration testing:

* FTP
* MySQL
* NFS
* SMB
* SMTP
* SSH
* Telnet

---

# Reports

The `reports/` directory contains documentation and evidence from practical labs and vulnerable environments.

Current reports include:

### Attacktive Directory

Active Directory enumeration and penetration testing work containing:

* Enumeration findings
* LDAP data
* BloodHound data
* Domain information
* User and group information
* Screenshots
* Command outputs
* Supporting evidence
* Full PDF report

### Metasploitable2

Practical penetration testing documentation containing:

* Enumeration
* Exploitation
* Screenshots
* Task documentation

---

# Learning Approach

The repository follows a practical approach to cybersecurity:

```text
Reconnaissance
      ↓
Enumeration
      ↓
Vulnerability Identification
      ↓
Exploitation
      ↓
Privilege Escalation
      ↓
Post-Exploitation
      ↓
Documentation
```

The goal is not only to memorize vulnerabilities, but to understand **how they fit into a real penetration testing workflow**.

---

# Goals

This repository serves as my personal cybersecurity knowledge base.

The main goals are to:

* Document what I learn
* Build reusable penetration testing methodologies
* Maintain useful checklists
* Collect payloads and wordlists
* Document practical exploitation techniques
* Develop automation scripts
* Keep CTF and lab write-ups
* Track my progress in cybersecurity
* Build a searchable reference for future engagements

---

# Disclaimer

This repository is intended for **educational and authorized security testing purposes only**.

Do not use the techniques, payloads, scripts, or methodologies contained in this repository against systems without explicit authorization.

The author is not responsible for any misuse of the information provided.

---

# Author

**Ey3du!tto0**

Penetration Testing Enthusiast

GitHub: [@Eyadeltaher](https://github.com/Eyadeltaher)
