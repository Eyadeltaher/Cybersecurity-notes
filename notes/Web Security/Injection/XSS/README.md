# Cross-Site Scripting (XSS) — Notes & Examples

This folder contains comprehensive notes and a full professional methodology for identifying, testing, and exploiting **Cross-Site Scripting (XSS)** vulnerabilities.  
All content is authored in LaTeX and exported as high-quality PDFs for learning and reference.


---

## Payloads
- [https://portswigger.net/web-security/cross-site-scripting/cheat-sheet](https://portswigger.net/web-security/cross-site-scripting/cheat-sheet)
- [https://github.com/payloadbox/xss-payload-list](https://github.com/payloadbox/xss-payload-list)

---

###  1. XSS-notes.pdf

This document provides a complete educational walkthrough of Cross-Site Scripting (XSS) — from basic theory to advanced exploitation. It’s written for students, pentesters, and web developers aiming to understand how XSS works and how to defend against it.

** Key sections**
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

>  **Use this document** to gain deep theoretical understanding and explore the reasoning behind modern XSS exploits.

---

###  2. XSS Methodology and Checklist.pdf

This companion document provides a **step-by-step assessment framework** designed for penetration testers and red-teamers. It includes checklists, testing workflows, and example payloads covering the entire lifecycle of an XSS vulnerability.

** Methodology Phases**
1. **Reconnaissance & Information Gathering**  

2. **Initial Testing & Context Identification**  

3. **Advanced Bypass Techniques**  

4. **DOM-based XSS Assessment**  

5. **CSP Analysis & Bypass**  

6. **Exploitation & Impact Assessment**  

7. **Verification & Reporting**  

>  **Use this checklist** during web assessments to ensure comprehensive coverage from discovery to verification.

---

###  Suggested Reading Order
 **Start with `XSS-notes.pdf`** → Understand the theory and core exploit mechanics  
 **Then read `XSS Methodology and Checklist.pdf`** → Apply structured testing in real engagements  

---

###  References & Resources
- [PortSwigger XSS Cheat Sheet](https://portswigger.net/web-security/cross-site-scripting/cheat-sheet)  
- [OWASP XSS Prevention Cheat Sheet](https://owasp.org/www-community/xss-prevention)  
- [Mozilla Content Security Policy (CSP) Guide](https://developer.mozilla.org/en-US/docs/Web/HTTP/CSP)  
- Others

---

## Where to go next (recommended)

* Read the PortSwigger XSS cheat sheet for additional payloads and defensive details: [https://portswigger.net/web-security/cross-site-scripting/cheat-sheet](https://portswigger.net/web-security/cross-site-scripting/cheat-sheet)
* Build a local lab (e.g. OWASP Juice Shop, DVWA) and practice the examples in a contained environment.
* Study Content Security Policy (CSP) and HttpOnly cookie usage to understand mitigations.
* Solve PortSwigger XSS labs (30)

