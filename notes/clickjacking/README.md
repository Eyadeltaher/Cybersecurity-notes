# Clickjacking (UI Redressing) — Notes & Methodology

Clickjacking, also known as a "UI Redress Attack," is an interface-based attack where an attacker tricks a user into clicking on a hidden or disguised element. The user believes they are interacting with a harmless page but unintentionally performs an action on a hidden or target website. This exploits user trust, active sessions, and browser behavior to execute unauthorized actions.

---

## Document 1: Clickjacking Notes PDF

### Key Sections

* **Introduction**

* **Vulnerability Preconditions**

* **Impact Analysis**

* **Common Vulnerable Areas**

* **Mitigation Headers**

* **Identification Techniques**

* **False Positives**

* **Exploitation Techniques**

---

### Use-Case Explanation

This document helps security testers and developers:

* Understand the mechanics and impact of clickjacking attacks
* Identify vulnerable endpoints and functions
* Build proof-of-concept exploits for testing purposes
* Apply practical mitigation strategies and verify protection

It is suitable for bug bounty hunters, penetration testers, and developers securing sensitive web applications.

---

## Document 2: Clickjacking Methodology / Checklist PDF

### Phases / Steps

1. **Reconnaissance & Scope Definition**

2. **Header Analysis**

3. **Vulnerability Confirmation**

4. **Exploitation Testing**

5. **Remediation Verification**

---

### Suggested Reading Order

1. **Clickjacking Notes PDF** – for foundational concepts, examples, and impact assessment
2. **Clickjacking Methodology / Checklist PDF** – for systematic testing and exploitation workflow

---

### References & Resources

* PortSwigger Web Security Academy — Clickjacking
* Firefox Add-on: Click-jacking by Daoud Youssef
* Burp Suite Clickbandit plugin

---

### Where to Go Next

* Practice in PortSwigger labs
* Test multi-step actions and prefilled form vectors
* Combine clickjacking with other vulnerabilities (XSS, CSRF)
* Implement and verify `X-Frame-Options` and `CSP frame-ancestors` headers
