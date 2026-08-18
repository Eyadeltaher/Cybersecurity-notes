Simple Mail Transfer Protocol. It is utilised to handle the sending of emails. In order to support email services, a protocol pair is required, comprising of SMTP and POP/.IMAP Together they allow the user to send outgoing mail and retrieve incoming mail, respectively.

==PORT 25==

The SMTP server performs three basic functions:
-  It verifies who is sending emails through the server.
-  It sends the outgoing mail
-  If the outgoing mail can't be delivered it sends the message back to the sender


### POP3 vs IMAP 
Both are protocols that let an email app communicate with a **mail server**.

Think:
```text
Email Server
     │
     ├── Your phone
     └── Your laptop
```

### POP3

**POP3 = Post Office Protocol version 3**

POP3 generally works like:
> **Download the emails from the server to your device.**

For example:
```text
Server
  │
  │ Download emails
  ▼
Laptop
```

Your email is mainly stored locally on the laptop.

If you read/delete an email on one device, those changes may **not automatically synchronize** with your other devices, depending on the POP3 configuration.

---

### IMAP
**IMAP = Internet Message Access Protocol**

IMAP works differently:
> **Keep the emails on the server and synchronize your devices with the server.**

For example:
```text
             Email Server
             /          \
            ↓            ↓
         Laptop        Phone
            ↕            ↕
         Synchronize with server
```

Suppose you read an email on your phone.

The server records:
```text
Email → Read
```

Then when you open your laptop, it synchronizes with the server and also shows:
```text
Email → Read
```

Same thing with deleting, moving, or marking emails.

### Easy way to remember

|POP3|IMAP|
|---|---|
|**Download** emails|**Synchronize** emails|
|Mainly local storage|Mainly server storage|
|Less convenient for multiple devices|Great for multiple devices|
|Older/simple approach|Modern/common approach|

**One important correction:** POP3 and IMAP don't transfer mail _between mail servers_. They primarily handle access between an **email client and a mail server**.

==NOTE== --> SMTP also works on both Windows and Linux.


# SMTP enumeration

### 1. Start Metasploit
```bash
msfconsole
```

---

### 2. Search for `smtp_version`

Inside Metasploit:
```text
search smtp_version
```

You should find something like:
```text
auxiliary/scanner/smtp/smtp_version
```

---

### 3. Select the module

```text
use auxiliary/scanner/smtp/smtp_version
```

Then see its options:
```text
show options
```

---

### 4. Set the target

Look for the option called:
```text
RHOSTS
```

Set it to your lab machine's IP:

```text
set RHOSTS <TARGET_IP>
```

Then run:
```text
run
```

You should get information about the SMTP server, including the **system mail name**.

---

### 5. Identify the MTA

The output should tell you something similar to:

```text
220 something.local ESMTP Postfix
```

The software after `ESMTP` is usually the **Mail Transfer Agent (MTA)**.

If you need to research it, search the exact product/version shown by Metasploit.

---

## SMTP username enumeration

### 6. Search for `smtp_enum`

Inside Metasploit:
```text
search smtp_enum
```

You should find:
```text
auxiliary/scanner/smtp/smtp_enum
```

Select it:
```text
use auxiliary/scanner/smtp/smtp_enum
```

Then:
```text
show options
```

---

### 7. Set the username wordlist

The lab gives you:
```text
/usr/share/wordlists/SecLists/Usernames/top-usernames-shortlist.txt
```

The option you need is:
```text
USER_FILE
```

Set it:
```text
set USER_FILE /usr/share/wordlists/SecLists/Usernames/top-usernames-shortlist.txt
```

If that file doesn't exist, check:
```bash
ls /usr/share/wordlists/SecLists/Usernames/
```

---

### 8. Set the other essential parameter

Again, you need:
```text
RHOSTS
```

Set it to the target:
```text
set RHOSTS <TARGET_IP>
```


You can verify everything with:
```text
show options
```

You should have something like:
```text
RHOSTS      10.112.153.177
USER_FILE   /usr/share/wordlists/SecLists/Usernames/top-usernames-shortlist.txt
```

---

### 9. Run the enumeration

```text
run
```

Metasploit will test usernames from the wordlist against the SMTP server and report usernames that appear to be valid.

**Important:** Don't use `exploit` here. These are **auxiliary scanner modules**, so `run` is the appropriate command.