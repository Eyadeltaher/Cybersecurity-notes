# Access Control — Notes & Examples

This folder contains comprehensive notes and a assessment methodology for identifying, testing, and exploiting **Access Control vulnerabilities** in web applications.
All content is authored in LaTeX and exported as high-quality PDFs for structured learning, practical testing, and long-term reference.

Access control issues are among the most critical web vulnerabilities and are a frequent root cause of account takeover, data exposure, and full application compromise.

---

## 1. Access control.pdf

This document provides a complete theoretical and practical foundation for understanding access control in modern web applications. It explains how authorization should work, why it commonly fails, and how attackers exploit these failures.

### Key sections

* **Core concepts**

* **Why access control vulnerabilities occur**

* **Where access control flaws appear**

* **Impact analysis**

* **Types of access control**

* **Common broken access control scenarios**

* **Insecure Direct Object References (IDOR)**

* **Advanced access control bypass techniques**

* **Practical attack examples**

> Use this document to build a strong conceptual understanding of access control and to recognize vulnerable patterns during real-world assessments.

---

## 2. Access Control Methodology & Checklist.pdf

This companion document provides a **structured, phase-based assessment methodology** for discovering and exploiting access control vulnerabilities during penetration tests and bug bounty engagements.

### Methodology phases

1. **Reconnaissance and application mapping**

2. **Authentication and session analysis**

3. **Vertical privilege escalation testing**

4. **Horizontal privilege escalation and IDOR**

5. **Platform and configuration bypasses**

6. **Multi-step workflow testing**

7. **Business logic and context-based testing**

8. **Automated and manual testing**

9. **Impact assessment and exploitation**

> Use this methodology as a thinking framework rather than a mechanical checklist to uncover complex authorization flaws and escalation chains.

---

## Suggested Reading Order

1. **Access control.pdf**
   Build a solid understanding of authorization concepts, vulnerability patterns, and exploitation techniques.

2. **Access Control Methodology & Checklist.pdf**
   Apply the concepts in a structured and systematic way during assessments.

---

## References & Resources

* OWASP Top 10 – Broken Access Control
* PortSwigger Web Security Academy – Access Control

---

## Where to Go Next (Recommended)

* Practice access control testing on intentionally vulnerable labs such as PortSwigger Web Security Academy.
* Always test authorization on **every request**, not just UI-visible functionality.
* Combine access control testing with recon and endpoint discovery techniques.
* Pay special attention to IDOR issues across APIs, mobile endpoints, and multi-step workflows.

