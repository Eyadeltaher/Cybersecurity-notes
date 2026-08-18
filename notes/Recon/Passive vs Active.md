## Passive Reconnaissance

Passive reconnaissance relies exclusively on publicly available information. No packets are sent to the target and no direct interaction occurs. It is analogous to observing the target territory from a safe distance using binoculars, without ever stepping onto their land.

Common passive activities include:
- Querying public records from open resolvers (A, MX, TXT, etc.).
- Searching certificate transparency logs (e.g., crt.sh) for subdomains and issued certificates.
- Reviewing job postings on LinkedIn or company career pages for tech stack hints.
- Reading public news, press releases, or leaked documents on paste sites.
- Checking exposed devices via search engines like Shodan or Censys.
- Scanning public GitHub repositories for hardcoded credentials or configuration files.

## Active Reconnaissance

Active reconnaissance requires direct engagement with the target. Your probes can be logged, detected, or blocked. It is analogous to walking up to the doors and windows to test locks, cameras, and alarms.

Common active activities include:

- Sending packets to discover live hosts (e.g. ICMP pings, ARP requests).
- Port scanning or service enumeration (Nmap, masscan).
- Interacting with web applications or APIs (fuzzing endpoints, Directory brute-forcing).
