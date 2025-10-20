# Cross-Site Scripting (XSS) — Notes & Examples

This folder contains comprehensive notes and a full professional methodology for identifying, testing, and exploiting **Cross-Site Scripting (XSS)** vulnerabilities.  
All content is authored in LaTeX and exported as high-quality PDFs for learning and reference.


---

## Payloads
- [https://portswigger.net/web-security/cross-site-scripting/cheat-sheet](https://portswigger.net/web-security/cross-site-scripting/cheat-sheet)
- [https://github.com/payloadbox/xss-payload-list](https://github.com/payloadbox/xss-payload-list)

---

### 📘 1. XSS-notes.pdf

This document provides a complete educational walkthrough of Cross-Site Scripting (XSS) — from basic theory to advanced exploitation. It’s written for students, pentesters, and web developers aiming to understand how XSS works and how to defend against it.

**🧩 Key sections**
- **Introduction to XSS:** Definition, causes, and impact on users  
- **Main types:** Stored (Persistent), Reflected, and DOM-Based XSS  
- **Source vs Sink:** Detailed explanation of data flow in the browser and how untrusted input reaches dangerous sinks  
- **Real-world attack surfaces:**
  - Uploading malicious **SVG** files  
  - Exploiting **Swagger UI** misconfigurations (versions 3.14.1 – 3.37.0)  
  - **AngularJS DOM XSS** and sandbox bypasses  
- **Methodology overview:** Practical discovery process using unique markers, page-source analysis, and WAF behavior testing  
- **Fuzzing techniques:** Using Burp Suite Intruder with XSS cheat sheets for tag + attribute fuzzing  
- **Exploitation walkthroughs:**
  - Cookie stealing  
  - Login credential theft  
  - Automatic vulnerability verification using **XSS.report**
- **CSP ( Content Security Policy ) section:**
  - How CSP works and why it matters  
  - Common directives and examples  
  - Step-by-step **CSP injection attack** walkthrough demonstrating how CSP misconfigurations can re-enable XSS execution  
- **Notes & tips:** Handling WAFs, jQuery detection, iframe exploitation, canonical link behavior, encoding techniques, and payload explanations

> 💡 **Use this document** to gain deep theoretical understanding and explore the reasoning behind modern XSS exploits.

---

### 🧾 2. XSS Methodology and Checklist.pdf

This companion document provides a **step-by-step assessment framework** designed for penetration testers and red-teamers. It includes checklists, testing workflows, and example payloads covering the entire lifecycle of an XSS vulnerability.

**⚙️ Methodology Phases**
1. **Reconnaissance & Information Gathering**  
   - Identify all user input points (GET, POST, cookies, headers, file uploads, APIs)  
   - Map client-side JavaScript sinks ( `innerHTML`, `eval`, `document.write` )  
   - Analyze CSP headers and allowed sources  

2. **Initial Testing & Context Identification**  
   - Insert unique markers and analyze HTML/JS contexts  
   - Detect context (HTML element, attribute, JS, URL, CSS)  
   - Run baseline payloads to classify injection behavior  

3. **Advanced Bypass Techniques**  
   - Tag and attribute fuzzing with Burp Intruder  
   - Encoding methods (HTML, URL, Unicode, multi-layer)  
   - JavaScript tricks — `/**/`, template literals, operator injection  

4. **DOM-based XSS Assessment**  
   - Source vs sink mapping  
   - Advanced AngularJS sandbox escapes and event-based bypasses  
   - SVG animation payloads  

5. **CSP Analysis & Bypass**  
   - Header inspection and directive testing  
   - Example of CSP directive injection (`;script-src-elem 'unsafe-inline'`)  

6. **Exploitation & Impact Assessment**  
   - Proof-of-concept payloads (cookie theft, credential capture, CSRF token stealing)  
   - Client-side validation bypass techniques  

7. **Verification & Reporting**  
   - Manual and automated verification methods  
   - Impact assessment guidelines (session hijack, privilege escalation)  
   - Final checklist for report completion  

> 🧩 **Use this checklist** during web assessments to ensure comprehensive coverage from discovery to verification.

---

### 🧷 Suggested Reading Order
1️⃣ **Start with `XSS-notes.pdf`** → Understand the theory and core exploit mechanics  
2️⃣ **Then read `XSS Methodology and Checklist.pdf`** → Apply structured testing in real engagements  

---

### 🔍 References & Resources
- [PortSwigger XSS Cheat Sheet](https://portswigger.net/web-security/cross-site-scripting/cheat-sheet)  
- [OWASP XSS Prevention Cheat Sheet](https://owasp.org/www-community/xss-prevention)  
- [Mozilla Content Security Policy (CSP) Guide](https://developer.mozilla.org/en-US/docs/Web/HTTP/CSP)  
- Others
---

## How to view / rebuild the notes

### Open the compiled PDF (recommended)

### Rebuild from LaTeX source (if you want to edit and recompile)

```bash
cd notes/XSS
pdflatex XSS-notes.tex
# (repeat pdflatex if needed for references)
```

You may need typical LaTeX toolchain packages (e.g. `texlive-latex-recommended`, `texlive-latex-extra`, etc.).

---

## Responsible use & disclaimer

These materials are provided solely for **educational, research, and defensive** purposes. Do **not** use the payloads, techniques, or examples against systems you do not own or do not have explicit permission to test. Unauthorized testing may be illegal and unethical.

---

## Where to go next (recommended)

* Read the PortSwigger XSS cheat sheet for additional payloads and defensive details: [https://portswigger.net/web-security/cross-site-scripting/cheat-sheet](https://portswigger.net/web-security/cross-site-scripting/cheat-sheet)
* Build a local lab (e.g. OWASP Juice Shop, DVWA) and practice the examples in a contained environment.
* Study Content Security Policy (CSP) and HttpOnly cookie usage to understand mitigations.
* Solve PortSwigger XSS labs (30)

