# Internet Message Access Protocol

### What is IMAP?

**IMAP = protocol used to access and manage emails stored on a mail server.**

Unlike POP3, emails **stay on the server** and are synchronized across devices.

**Think:**

> IMAP = Email stays on server + Sync across devices

---

## Ports

|Port|Service|Security|
|---|---|---|
|`143`|IMAP|Plaintext / STARTTLS|
|`993`|IMAPS|SSL/TLS|

**Remember:**
```text
143  → IMAP
993  → IMAPS (encrypted)
```

---

# 1. Check if IMAP is Open

```bash
nmap -p 143,993 <IP>
```

Example:
```bash
nmap -p 143,993 10.112.156.234
```

With service detection:
```bash
nmap -sV -p 143,993 <IP>
```

**`-sV`** → Detect service/version.

---

# 2. Connect to IMAP

For plaintext IMAP:
```bash
telnet <IP> 143
```

Example:
```bash
telnet 10.112.156.234 143
```

If successful, you'll see something like:

```text
* OK ... IMAP4rev1 ... STARTTLS ...
```

For encrypted IMAPS:
```bash
openssl s_client -connect <IP>:993
```

This creates an SSL/TLS connection to port `993`.

---

# 3. IMAP Commands

### Important concept: Tags

Every IMAP command needs a **tag**.

Example:
```text
c1 LOGIN username password
c2 LIST "" "*"
c3 EXAMINE INBOX
c4 LOGOUT
```

The tag can be almost anything:
```text
A001
A002
A003
```

**Remember:**

> Tag = identifier used to match commands with server responses.

---

## LOGIN

```text
c1 LOGIN username password
```

Authenticates to the mailbox.

Example:
```text
c1 LOGIN frank D2xc9CgD
```

 On plaintext IMAP, credentials can potentially be exposed to someone sniffing the traffic.

---

## LIST

```text
c2 LIST "" "*"
```

Lists available mailboxes/folders.

Example:
```text
* LIST (...) "INBOX"
* LIST (...) "INBOX.Sent"
* LIST (...) "INBOX.Drafts"
* LIST (...) "INBOX.Trash"
```

**Useful for reconnaissance** because it reveals the mailbox structure.

---

## SELECT

```text
c3 SELECT INBOX
```

Opens a mailbox for **read/write** operations.

> SELECT = open the folder

---

## EXAMINE

```text
c3 EXAMINE INBOX
```

Opens a mailbox **read-only**.

> EXAMINE = inspect the folder

---

## FETCH

```text
c4 FETCH 1 BODY[]
```

Retrieves the contents of message `1`.

Example:

```text
c4 FETCH 1 BODY[]
```

Useful when manually inspecting emails.

---

## SEARCH

```text
c5 SEARCH ALL
```

Searches messages.

Some useful examples:

```text
c5 SEARCH ALL
c5 SEARCH FROM "admin"
c5 SEARCH SUBJECT "password"
c5 SEARCH UNSEEN
```

**Remember:**

> SEARCH = find interesting emails

---

## STORE

```text
c6 STORE 1 +FLAGS (\Seen)
```

Changes flags on an email.

For example, marks message `1` as **read**.

---

## LOGOUT

```text
c7 LOGOUT
```

Ends the IMAP session.

---

# Common IMAP Commands — Cheat Sheet

|Command|Purpose|
|---|---|
|`LOGIN user pass`|Login|
|`LIST "" "*"`|List folders|
|`SELECT INBOX`|Open mailbox read/write|
|`EXAMINE INBOX`|Open mailbox read-only|
|`FETCH 1 BODY[]`|Read message|
|`SEARCH ALL`|Search emails|
|`STORE 1 +FLAGS (\Seen)`|Mark email as read|
|`LOGOUT`|Exit|

---

# 4. Check Server Capabilities

When you connect, the server may respond with:

```text
* OK [CAPABILITY IMAP4rev1 UIDPLUS STARTTLS IDLE ACL ...]
```

Look for:

### `IMAP4rev1`

IMAP version supported.

### `STARTTLS`

The server can upgrade a plaintext connection to TLS.

### `IDLE`

Server can notify the client when new mail arrives.

### `ACL`

Access Control Lists are supported.

**Pentesting tip:**

> Always read the initial banner/capabilities — they reveal supported features.

---

# IMAP vs POP3

|                  | IMAP        | POP3               |
| ---------------- | ----------- | ------------------ |
| Server storage   | Emails stay | Usually downloaded |
| Multiple devices | Excellent   | Limited            |
| Synchronization  | YES         | NO                 |
| Default port     | `143`       | `110`              |
| Secure port      | `993`       | `995`              |

**Easy memory:**

> **IMAP = Keep & Sync**  
> **POP3 = Download**

---

# Security / Pentesting Importance

Compromised IMAP credentials can be valuable because an attacker may be able to:

- Read old emails
- Monitor new emails
- Search for passwords/secrets
- Find password-reset emails
- Discover internal information
- Identify other users/services
- Obtain sensitive documents from attachments
    
### Important enumeration targets

When you gain IMAP access, look for:
```text
INBOX
Sent
Drafts
Trash
Templates
```

Especially interesting:
```text
Sent     → previous communications
Drafts   → potentially sensitive unfinished messages
INBOX    → credentials/reset links/instructions
```

