# 🛡️ Cybersecurity Notes

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](./LICENSE)
[![Last Commit](https://img.shields.io/github/last-commit/Eyadeltaher/Cybersecurity-notes)](https://github.com/Eyadeltaher/Cybersecurity-notes/commits/main)
[![Topics](https://img.shields.io/github/topics/Eyadeltaher/Cybersecurity-notes?style=flat)](https://github.com/Eyadeltaher/Cybersecurity-notes)

A **comprehensive and structured collection** of web security notes, practical examples, payloads, scripts, and curated wordlists.  
Designed for **learning, reference, and practical penetration testing**.

---

## 📂 Repository Overview

The repository is organized by vulnerability category, tool, and resource type:

- [**Access Control**](notes/Access%20control) 🔐 – Notes, methodology, privilege bypass  
- [**CSRF**](notes/CSRF) 🎯 – Cross-Site Request Forgery notes & methodology  
- [**General**](notes/general) 📘 – Web security fundamentals & Google Dorks  
- [**Information Disclosure**](notes/Information%20Disclosure) 💡 – Notes & write-ups  
- [**Recon**](notes/Recon) 🕵️‍♂️ – Web reconnaissance methodology & workflow  
- [**SQLi**](notes/SQLi) 💉 – SQL Injection: methodology, examples, scripts  
- [**Tools**](notes/Tools) 🧰 – Dirsearch & httpx usage guides  
- [**WordLists**](notes/WordLists) 📝 – Curated wordlists for fuzzing and enumeration  
- [**XSS**](notes/XSS) ✨ – Cross-Site Scripting methodology, checklist, and payloads  

---

## 📚 Sections Breakdown

### 🔐 Access Control
- Privilege escalation & bypass techniques  
- IDOR testing  
- Horizontal & vertical access bypass  
- PDFs: `Access control.pdf`, `Access Control Methodology.pdf`

### 🎯 CSRF
- CSRF attack scenarios & anti-CSRF tokens  
- Testing methodology & examples  
- PDF: `CSRF-notes.pdf`

### 📘 General
- Web security fundamentals  
- Best practices & secure development tips  
- Google Dorks references: `google Dorks.pdf`, `googleHacking.pdf`

### 💡 Information Disclosure
- Sources & methods of information leaks  
- Real-world inspired write-ups  
- PDFs: `information disclosure.pdf`, `information disclosure write-ups notes.pdf`

### 🕵️‍♂️ Recon
- Web application reconnaissance methodology  
- Asset discovery, service fingerprinting, tools workflow  
- PDF: `Web Application Reconnaissance.pdf`

### 💉 SQLi (SQL Injection)
- Error-based, blind, time-based SQLi  
- Auth bypass techniques & payloads  
- Example Python scripts:  
  - `sqli_blind_error-based-example.py`  
  - `sqli_timebased-example.py`  
- PDF: `SQLi-notes.pdf`

### 🧰 Tools
**Dirsearch** – Directory & file fuzzing, options, methodology  
**httpx** – Host probing, asset discovery, example flags  
PDFs included for both

### 📝 WordLists
Organized collections for fuzzing, enumeration, and pentesting:  
- API endpoints, objects, actions  
- Context-specific lists (admin, debug, logs, setup)  
- Programming-language-specific lists (PHP, JSP, ASP.NET, Go, Rails, etc.)  
- Raft & DirBuster lists  
- Fuzzing lists: `Logins.fuzz.txt`, `Passwords.fuzz.txt`  

### ✨ XSS (Cross-Site Scripting)
- Notes & methodology  
- Checklist for testing  
- Payload examples & SVG test file  
- PDFs: `XSS-notes.pdf`, `XSS Methodology and Checklist.pdf`

---

## 🚀 How to Use

### Viewing Notes
- Open PDFs in `notes/<topic>/` for reading.

### Editing / Compiling LaTeX Notes
```bash
cd notes/<topic>
pdflatex filename.tex
````

### Practical Testing

* Use included scripts and wordlists with tools like `ffuf`, `gobuster`, `dirsearch`, or Burp Suite.

---

## 📌 Purpose

This repository is designed to:
✔ Serve as a personal knowledge base
✔ Provide structured penetration testing methodology
✔ Include high-quality wordlists & payloads
✔ Offer ready-to-use scripts for practical learning

---

## ⚠️ Disclaimer

For **educational purposes only**.
Do **not** use any scripts, payloads, or methodologies for unauthorized testing.

---

## 👤 Author

**Eyad Eltaher** – Web Security | Penetration Testing | Bug Bounty Enthusiast

---

