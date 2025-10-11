# Cross-Site Scripting (XSS) — Notes & Examples

Author: **Eyad Islam El-Taher**  
Date: Friday, October 3, 2025

This folder contains a detailed technical writeup about Cross-Site Scripting (XSS): types, attack vectors, exploitation examples, payload strategies, practical methodology. The source material and compiled PDF are included for study and safe, ethical practice.

---

## Files in this folder
- `XSS-notes.tex` — LaTeX source (editable).
- `XSS-notes.pdf` — Compiled PDF (readable version). :contentReference[oaicite:1]{index=1}
- `evilsvgfile.svg` — Example SVG payload demonstrating script execution via an image file.
- `cheatsheet.md` — Quick reference / payload snippets.

---

## Summary (what's inside)
The notes cover:
- XSS fundamentals: what XSS is and where it occurs (cookies, form inputs, headers, GET/POST parameters).
- XSS types: **Stored (persistent)**, **Reflected**, and **DOM-based** XSS, with clear examples and URLs/payload forms.
- Sources vs Sinks: how attacker-controlled input flows from a source into dangerous sinks (`innerHTML`, `document.write`, `eval`, `setAttribute`, `location = 'javascript:...'`, etc.).
- Realistic exploitation techniques:
  - SVG file payloads and how browsers treat `image/svg+xml`.
  - Swagger-UI attack vectors (config, `url`, `configUrl` parameters).
  - AngularJS/templating pitfalls and DOM XSS payloads.
  - Using Burp Collaborator to exfiltrate cookies or credentials.
- Practical methodology for discovery and exploitation (unique markers, view-source analysis, WAF fuzzing, Burp Intruder workflows).
- Bypass strategies (encoding, event fuzzing, tag/attribute fuzzing, multi-layer encoding).
- Attack impact: session hijacking, credential theft, CSRF token theft leading to account takeover.
- Defensive advice: HttpOnly cookies, CSP, input validation and output encoding, and secure handling of sensitive tokens.

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

