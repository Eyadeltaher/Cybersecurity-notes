#  Cybersecurity Notes

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](./LICENSE)
[![Last Commit](https://img.shields.io/github/last-commit/Eyadeltaher/Cybersecurity-notes)](https://github.com/Eyadeltaher/Cybersecurity-notes/commits/main)

A **comprehensive and structured collection** of web security notes, methodologies, payloads, scripts, tools documentation, and curated wordlists.  
Designed for **learning, reference, CTF practice, and practical penetration testing**.

---

##  Repository Overview

The repository is organized by vulnerability category, tooling, and resource type:

- [**Access Control**](notes/Access%20control)  – Authorization flaws, IDOR, privilege escalation
- [**Authentication**](notes/Authentication)  – Authentication flaws, notes, methodology
- [**Clickjacking**](notes/clickjacking)  – UI redressing attacks & testing examples  
- [**CORS**](notes/CORS)  – CORS misconfigurations & exploitation  
- [**CSRF**](notes/CSRF)  – Cross-Site Request Forgery notes & methodology  
- [**Information Disclosure**](notes/Information%20Disclosure)  – Data leakage techniques & notes  
- [**Path Traversal**](notes/Path%20traversal)  – Directory traversal vulnerabilities & payloads  
- [**Recon**](notes/Recon)  – Web reconnaissance methodology & workflow  
- [**SQLi**](notes/SQLi)  – SQL Injection techniques, payloads, and scripts  
- [**XSS**](notes/XSS)  – Cross-Site Scripting methodology, checklists & payloads  
- [**Tools**](notes/Tools)  – Tool usage notes (dirsearch, httpx, etc.)  
- [**WordLists**](notes/WordLists)  – Curated wordlists for fuzzing & enumeration  
- [**CTFs & Write-Ups**](notes/CTFs%20%26%20Write-Ups)  – CTF notes, write-ups & practical exploitation  

---

###  CTFs & Write-Ups
- Notes taken from **reading high-quality CTF write-ups**
- Personal notes from **CTFs I personally solved**
- Practical payloads & exploitation techniques  
- Focused on learning patterns, tricks, and real-world skills

---

##  How to Use

###  Viewing Notes
Open PDFs inside:
```
notes/<topic>/
````

### 🛠️ Editing / Compiling LaTeX Notes
```bash
cd notes/<topic>
pdflatex filename.tex
````


---

##  Purpose

This repository aims to:
* Act as a personal cybersecurity knowledge base
* Provide structured penetration testing methodologies
* Preserve high-quality wordlists & payloads
* Support CTFs and bug bounty learning

---

##  Disclaimer

This repository is for **educational purposes only**.
Do **NOT** use any techniques, payloads, or scripts on systems you do not own or have explicit permission to test.

---

##  Author

**Eyad Eltaher**

Penetration Tester • Bug Bounty Hunter
