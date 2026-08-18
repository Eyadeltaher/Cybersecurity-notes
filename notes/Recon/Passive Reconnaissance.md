
# 1. Whois

WHOIS is a query/response protocol defined in [3912 (opens in new tab)](https://www.ietf.org/rfc/rfc3912.txt). WHOIS servers listen on **port 43** and provide registration details for domain names. The **domain registrar** maintains these records for the domains they lease.

From a WHOIS response, the following details may be available (when not redacted):

- **Registrar**: The company (e.g., Namecheap, GoDaddy) that registered the domain.
- **Registrant contact information**: Name, organisation, address, phone, and email. However, **privacy services** (standard since 2018) usually replace this with "Withheld for Privacy" or similar.
- **Dates**: Creation (registration), Updated (last change), and Expiration (renewal deadline).
- **Name servers**: The servers authoritative for the domain.
- **Status codes**: For example, `clientTransferProhibited` indicates the domain is locked against unauthorised transfers.
- **Abuse contacts**: The registrar's email and phone for reporting issues.

### WHOIS Is Being Replaced By RDAP

As of 28 January 2025, ICANN officially sunsetted the traditional WHOIS protocol for generic top-level domains (gTLDs) in favour of the **Registration Data Access Protocol (RDAP)**. RDAP is the modern successor: it uses HTTPS (secure), returns structured JSON (machine-readable and consistent), supports internationalisation, provides better privacy controls (differentiated access), and aligns with current data protection rules. While legacy `whois` clients still work (often via failover or older servers), RDAP is now the authoritative standard. Many tools and browsers redirect to RDAP automatically, and command-line access is straightforward with `curl` or dedicated clients like OpenRDAP.

```bash
whois tryhackme.com

curl -s https://rdap.verisign.com/com/v1/domain/tryhackme.com | jq .
```
The `jq` utility formats the JSON output for readability

NOTE --> there are many websites provide the whois service


---

# 2. dig & nslookup

querying records, which is still fully **passive** because the queries go to public or open resolvers, not to the target's servers directly.

`nslookup` and `dig`. Both query DNS, but `dig` is the modern, preferred option. It provides cleaner output, displays TTL values by default (showing how long records are cached), and is more reliable for complex queries and scripting. `nslookup` is covered here for compatibility, since you will encounter it in older documentation and on Windows systems, but `dig` should be your default tool.

A DNS TTL (Time-to-Live) value is ==a setting measured in seconds that tells caching servers how long to store a DNS record==. Common values range from 300 seconds (5 minutes) for fast updates to 86,400 seconds (24 hours) for stable, long-term caching. 

Common TTL Values
- **300 seconds (5 minutes):** Short lifespan; used when you plan to change server IPs soon.
- **3,600 seconds (1 hour):** Balanced choice; standard for general records.
- **86,400 seconds (24 hours):** Long lifespan; reduces server load for static sites. 

Pros and Cons
- **Short TTL:** Updates spread fast across the internet, but it causes more load on authoritative servers.
- **Long TTL:** Speeds up lookups and reduces server traffic, but changes take a long time to take effect globally.


**Common DNS record types**

|Record|Simple meaning|Example|
|---|---|---|
|**A**|Domain → IPv4 address|`example.com → 192.0.2.10`|
|**AAAA**|Domain → IPv6 address|`example.com → 2001:db8::10`|
|**CNAME**|Domain → another domain|`www.example.com → example.com`|
|**MX**|Where to send emails|`example.com → mail.example.com`|
|**NS**|Which DNS servers manage the domain|`example.com → ns1.example.com`|
|**TXT**|Text/information about the domain|SPF, verification, etc.|
|**PTR**|IP address → domain name|`192.0.2.10 → example.com`|
|**SOA**|Main information about the DNS zone|Primary DNS server, serial, timers|
|**SRV**|Where a specific service is located|`_sip._tcp.example.com → sip.example.com:5060`|
|**CAA**|Which Certificate Authorities can issue certificates|`example.com → Let's Encrypt`|

### 3. CNAME — "This name is another name"

Suppose:

```text
www.example.com → example.com
```

You can access both:

```text
example.com
www.example.com
```

but `www` doesn't necessarily have its own IP.

It basically says:

> "If you're looking for `www.example.com`, look at `example.com`."

---

### 4. MX — "Where does email go?"

This is extremely important for email.

For:

```text
eyad@example.com
```

DNS needs to know:

> "Which server handles email for `example.com`?"

An MX record might say:

```text
example.com → mail.example.com
```

Then:

```text
mail.example.com → 192.0.2.50
```

So the flow is:

```text
Email
  ↓
example.com
  ↓
MX record
  ↓
mail.example.com
  ↓
IP address
```

---

### 5. NS — "Who is responsible for this DNS zone?"

NS records tell you which DNS servers are authoritative for the domain.

For example:

```text
example.com

NS → ns1.example.com
NS → ns2.example.com
```

Meaning:

> "Ask these DNS servers for the official DNS information about `example.com`."

This becomes particularly important when you're studying **DNS reconnaissance**.

---
### 7. PTR — "Who owns this IP?"

Most records work:

```text
Domain → IP
```

PTR works in the opposite direction:

```text
IP → Domain
```

For example:

```text
192.0.2.10 → server.example.com
```

This is called **reverse DNS**.

Useful during reconnaissance because you can sometimes discover the hostname associated with an IP.

---

### 8. SOA — "The zone's main information"

SOA means **Start of Authority**.

It contains important information about the DNS zone, such as:

```text
Primary DNS server
Zone administrator
Serial number
Refresh time
Retry time
Expire time
Minimum/negative TTL
```

You don't usually memorize every field at first.

Think:

> **SOA = metadata about the DNS zone itself.**

---

### 9. SRV — "Where is this service?"

SRV records tell DNS where a **specific service** is running.

For example:

```text
_sip._tcp.example.com
```

could point to:

```text
sip.example.com:5060
```

So SRV answers:

> "Which server and port provide this service?"

You'll see these with things like:
- SIP
- XMPP
- LDAP
- Microsoft services
- VoIP
    

---

### 10. CAA — "Who can issue my SSL certificate?"

CAA records control which **Certificate Authorities (CAs)** are allowed to issue certificates for a domain.

For example:

```text
example.com CAA → Let's Encrypt
```

Meaning roughly:

> "Only this CA is authorized to issue certificates for this domain."

---

## The ones you should focus on first

Since you're learning **DNS/network security**, I'd prioritize them like this:

```text
A       → IPv4
AAAA    → IPv6
CNAME   → Alias
MX      → Email
NS      → DNS servers
TXT     → Verification / SPF / security information
PTR     → Reverse DNS
SOA     → Zone information
SRV     → Services
CAA     → Certificate authorities
```

---

```bash
nslookup chicken-road2.app
dig  chicken-road2.app
```

**Privacy tip**: Use public resolvers like `1.1.1.1` (which supports DNS over HTTPS and DNS over TLS) to avoid your ISP logging your queries.

---


```bash
dnsenum domain.com  --> enum for DNS records and try DNS Zone Transfer
```

DNS Zone Transfer Misconfiguration

### 1. What is a DNS Zone Transfer?

A **zone transfer** is a mechanism for copying DNS records from a primary DNS server to a secondary DNS server.

For example, suppose `example.com` has:

```text
example.com
├── www       → 10.0.0.10
├── mail      → 10.0.0.20
├── vpn       → 10.0.0.30
├── dev       → 10.0.0.40
└── internal  → 10.0.0.50
```

The secondary DNS server needs these records, so the primary can provide them through:
- **AXFR** → full zone transfer
- **IXFR** → incremental zone transfer
    
Normally, zone transfers should only be allowed between **trusted DNS servers**.

---

### 2. What is the misconfiguration?

The problem occurs when the DNS server allows **anyone** to request a zone transfer.

Conceptually:

```text
Attacker
   │
   │  "Give me the zone for example.com"
   ▼
DNS Server
   │
   │  AXFR
   ▼
Entire DNS Zone
```

Instead of getting only a normal DNS response:

```text
www.example.com → 10.0.0.10
```

the attacker may receive many records at once:

```text
www.example.com       10.0.0.10
mail.example.com      10.0.0.20
vpn.example.com       10.0.0.30
dev.example.com       10.0.0.40
git.example.com       10.0.0.50
internal.example.com  10.0.0.60
...
```

---

### 3. Why is this dangerous?
The main issue is **information disclosure**.
A successful zone transfer can reveal:
- Internal hostnames
- Subdomains
- IP addresses
- Mail servers
- Development/staging environments
- VPN infrastructure
- Administrative systems
- Naming conventions
- Sometimes internal/private network information
    
---

# 3. DNS to Subdomain enum

One well-known free tool is **[DNSDumpster (opens in new tab)](https://dnsdumpster.com/)**. It aggregates public DNS data from sources such as search engine caches, zone transfer databases, and certificate records. It does not perform brute-force enumeration, which means it remains fully passive. The results include subdomains and hosts, resolved IPs with geolocation, MX, TXT, and CNAME records, and visual maps showing the relationships between these.


**amass** **& subfinder** **& assetfinder**

```bash
amass enum -passive -d target.com
amass enum -d example.com --> More extensive enumeration
amass subs -names -d target.com --> to show o/p

subfinder -d target.com -all -recursive -o subfinder.txt
assetfinder --subs-only target.com > assetfinder.txt
```

Amass can combine multiple sources and techniques to build a larger picture.
Subfinder — fast passive discovery

https://www.subdomain.center/
https://viewdns.info/

to combine all
```bash
cat subfinder.txt amass.txt crt.txt | sort -u > all-subdomains.txt
```

# 4. Shodan and FOFA

Think of **Shodan and FOFA as “what is exposed on the Internet?” tools**, rather than pure subdomain finders.


```
Domain
  ↓
Subfinder / Amass / crt.sh
  ↓
Subdomains
  ↓
Resolve → IPs
  ↓
Shodan / FOFA
  ↓
Exposed ports + services + technologies
```


---

## 1. Shodan

[Shodan](https://www.shodan.io/)

### Start with a domain

```text
hostname:example.com
```

This searches for hosts whose hostname matches the domain.

You might discover:

```text
api.example.com
vpn.example.com
mail.example.com
dev.example.com
```

---

## Most important Shodan filters

### `hostname`

Probably the first one you should learn.

```text
hostname:example.com
```

Find hosts associated with the hostname.

---

### `domain`

```text
domain:example.com
```

Useful for finding assets associated with a domain.

---

### `ip`

If you've discovered an IP:

```text
ip:203.0.113.10
```

You can investigate what Shodan knows about that host.

---

### `port`

Find hosts exposing a particular port:

```text
port:8080
```

Combine it with your authorized target:

```text
hostname:example.com port:8080
```

---

### `http.title`

Search by webpage title:

```text
http.title:"Dashboard"
```

You can combine filters:

```text
hostname:example.com http.title:"Dashboard"
```

---

### `http.server`

Search for a particular web server:

```text
http.server:"nginx"
```

For example:

```text
hostname:example.com http.server:"nginx"
```

---

### `product`

Search for a particular product/service:

```text
product:"Apache httpd"
```

---

### `org`

Search an organization:

```text
org:"Example Corporation"
```

This can be useful when the company owns multiple domains/IP ranges.

---

### `ssl`

Shodan has useful SSL/TLS information.

For example:

```text
ssl:"example.com"
```

You can use certificate information to discover infrastructure that isn't obvious from DNS.

---

# A useful Shodan workflow

Suppose you're authorized to assess:

```text
example.com
```

Start:

```text
hostname:example.com
```

You find:

```text
api.example.com → 203.0.113.10
vpn.example.com → 203.0.113.20
```

Then investigate the IP:

```text
ip:203.0.113.10
```

Look at:

```text
Ports
Services
HTTP information
TLS certificate
Software/product
Banners
```

Then you can ask:

> What is this server actually exposing?

That's the real value of Shodan.

---

# 2. FOFA

[FOFA](https://fofa.info/)

FOFA works similarly but its query language is particularly useful for combining asset attributes.

## Most important FOFA searches

### Domain

```text
domain="example.com"
```

This is one of the first searches to try.

---

### Host

```text
host="example.com"
```

Useful when you're interested in a particular hostname/domain.

---

### IP

```text
ip="203.0.113.10"
```

Investigate an individual IP.

---

### Port

```text
port="8080"
```

Combine with your target:

```text
domain="example.com" && port="8080"
```

---

### HTTP title

```text
title="Dashboard"
```

For an authorized target:

```text
domain="example.com" && title="Dashboard"
```

---

### Server

```text
server="nginx"
```

Combined:

```text
domain="example.com" && server="nginx"
```

---

### Technology

FOFA can search technology fingerprints.

For example:

```text
domain="example.com" && app="WordPress"
```

This is useful for understanding the technology stack.

---

### Organization

```text
org="Example Corporation"
```

Useful when investigating an organization's broader infrastructure.

---

# The searches I'd memorize

Don't try to memorize 50 different operators.

### Shodan

```text
hostname:example.com
domain:example.com
ip:1.2.3.4
port:443
http.title:"..."
http.server:"..."
org:"..."
product:"..."
```

### FOFA

```text
domain="example.com"
host="example.com"
ip="1.2.3.4"
port="443"
title="..."
server="nginx"
app="..."
org="..."
```

---

# When should you actually use them?

###  Don't start with Shodan/FOFA

If your goal is:

> "Find every possible subdomain."

Start with:

```text
crt.sh
Subfinder
Amass
```

---

###  Use them after discovering infrastructure

For example:

```text
example.com
     ↓
Subfinder
     ↓
api.example.com
dev.example.com
vpn.example.com
     ↓
DNS resolution
     ↓
203.0.113.10
203.0.113.20
203.0.113.30
     ↓
Shodan / FOFA
     ↓
Ports + services + technologies
```

Now you're moving from **DNS enumeration → attack-surface discovery**.

---

## One particularly useful trick

Don't only search for the domain.

Suppose:

```text
example.com → 203.0.113.10
```

Search the IP in Shodan/FOFA.

You may discover that the same IP has:

```text
api.example.com
dev.example.com
old.example.com
```

or other assets associated with it.

So you can pivot:

```text
Domain
  ↓
Subdomain
  ↓
IP
  ↓
Shodan / FOFA
  ↓
Other hostnames / services
```

That's the part that makes these tools powerful for reconnaissance.