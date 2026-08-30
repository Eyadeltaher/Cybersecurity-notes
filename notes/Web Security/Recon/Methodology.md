 Rootx Recon Methdology  
 
(step1):

-Passive Subdomain Enumeration:

subfinder:
subfinder -d example.com -o Subs01.txt
subfinder -dL example.com -o Subs01.txt
subfinder -d example.com -all -recursive -o Subs01.txt
---------------------------------------------------------------------------------------------

Assetfinder:
echo example.com | assetfinder -subs-only > Subs02.txt
---------------------------------------------------------------------------------------------

amass:
amass enum -d example.com -o Subs03.txt
amass enum -d example.com -brute -w wordlist.txt -o Subs03.txt
---------------------------------------------------------------------------------------------

subenum:
./subenum.sh -d example.com -u wayback,crt,abuseipdb,Findomain,Subfinder,Amass,Assetfinder -o Subs04.txt
./subenum.sh -l targets.txt -u wayback,crt,abuseipdb,Findomain,Subfinder,Amass,Assetfinder -o Subs04.txt
---------------------------------------------------------------------------------------------

findomain:
findomain -t example.com -u Subs05.txt
---------------------------------------------------------------------------------------------

chaos:
export PDCP_API_KEY=your_api_key_here
chaos -d example.com -o Subs06.txt
---------------------------------------------------------------------------------------------

github-subdomains:
github-subdomains -d example.com -t YOUR_GITHUB_TOKEN
https://github.com/settings/tokens
------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

-Active Subdomain Enumeration/Bruteforce:

dnscan:
python dnscan.py -d example.com -w wordlist.txt -t 300 | tee /home/kali/Subs07.txt
---------------------------------------------------------------------------------------------

puredns:
puredns bruteforce wordlist.txt example.com -r resolvers.txt
sudo wget https://raw.githubusercontent.com/trickest/resolvers/main/resolvers.txt
---------------------------------------------------------------------------------------------

dnsx:
dnsx -silent -d example.com -w wordlist.txt
------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

-Subdomain Fuzzing:

ffuf:
ffuf -u https://FUZZ.example.com -w wordlist.txt
ffuf -u https://FUZZ.hacked.example.com -w wordlist.txt
ffuf -u https://FUZZ-example.com -w wordlist.txt
ffuf -u https://FUZZ-hacked.example.com -w wordlist.txt
ffuf -u https://hacked-FUZZ.example.com -w wordlist.txt
ffuf -u https://FUZZwww.example.com -w wordlist.txt
------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

-Virtual Host Enumeration:

Virtualhost / Private enum

ffuf -u https://example.com -w wordlist.txt -H "Host: FUZZ.example.com"
ffuf -u http://<ip> -w wordlist.txt -H "Host: FUZZ.example.com"

ping example.com
sudo nano /etc/hosts
192.1.2.3 test.example.com
------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

-Infrastructure Discovery:

https://bgp.he.net

asnmap:
asnmap -a AS17012

whois:
whois -h whois.radb.net AS17012

dnsx PTR:
echo 66.211.170.0/23 | dnsx -silent -resp-only -ptr
---------------------------------------------------------------------------------------------

hakrevdns:
hakrevdns -d example.com -R resolvers.txt
---------------------------------------------------------------------------------------------

magicrecon:
./magicrecon.sh -l targets.txt --all
------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

-Certificate Transparency Subdomains(SSL):

curl -s "https://crt.sh/?q=%25.example.com&output=json" \
| jq -r '.[].name_value' \
| sed 's/\*\.//g' \
| tr '\n' ',' | tr ',' '\n' \
| grep -oE "[A-Za-z0-9._-]+\.example\.com" \
| sort -u
------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

-OSINT Sources(subdomains+info):

https://securitytrails.com + https://www.ultimatedomains.com/extract-domains.php
https://shrewdeye.app
https://subdomainfinder.c99.nl
https://netlas.io
https://urlscan.io
https://otx.alienvault.com
https://search.censys.io
https://www.virustotal.com
https://www.favihash.com
https://crt.sh
https://bgp.he.net
https://www.shodan.io + asn:AS8300
https://search.dnslytics.com/cidr
https://viewdns.info/reverseip/?host=
------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

-DNS Wordlists:

/usr/share/wordlists/seclists/Discovery/DNS/bitquark-subdomains-top100000.txt
/usr/share/wordlists/seclists/Discovery/DNS/dns-Jhaddix.txt
/usr/share/wordlists/seclists/Discovery/DNS/subdomains-top1million-110000.txt
/usr/share/wordlists/commonspeak2-wordlists-master/subdomains/subdomains.txt
/usr/share/wordlists/commonspeak2-wordlists-master/subdomains/fierce-hostlist.txt
/usr/share/wordlists/best-dns-wordlist.txt
sudo wget https://wordlists-cdn.assetnote.io/data/manual/best-dns-wordlist.txt
------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
STEP(2):

-Merge & Remove Duplicates

anew:
cat Subs*.txt | anew | tee AllSubs.txt
wc AllSubs.txt
------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
STEP(3):

-Alive Host Detection

httpx:
cat AllSubs.txt | httpx -o AliveSubs.txt

cat AllSubs.txt | httpx -status-code -content-length -web-server -title -follow-redirects

cat AllSubs.txt | httpx -status-code -content-length -web-server -title -follow-redirects -match-code 200

cat AllSubs.txt | httpx -status-code -content-length -web-server -title -follow-redirects -filter-code 400

404 â†’ wayback + fuzz
403 â†’ try bypass
------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
STEP(4):

-URL Discovery

waybackurls:
cat AliveSubs.txt | waybackurls > WB1.txt
---------------------------------------------------------------------------------------------

waymore:
waymore -i AliveSubs.txt -mode U -l 1000 -from 2021 -oU WM1.txt
---------------------------------------------------------------------------------------------

gau:
cat AliveSubs.txt | gau --threads 200 > GAU1.txt
---------------------------------------------------------------------------------------------

gauplus:
gauplus -t 200 -random-agent < AliveSubs.txt > GAU2.txt
---------------------------------------------------------------------------------------------

hakrawler:
cat AliveSubs.txt | hakrawler -subs -u -insecure > HK1.txt
---------------------------------------------------------------------------------------------

katana:
katana -u AliveSubs.txt -jc -kf all -d 5 -headless -fx -aff -fs rdn -f url -silent > KTN1.txt
echo "example.com" | katana
---------------------------------------------------------------------------------------------

gospider:
gospider -S AliveSubs.txt -t 20 -d 3 --js --sitemap --robots -o GS1.txt
gospider -S httpx.txt | sed -n 's/.*\(https:\/\/[^ ]*\)]*.*/\1/p' >> GS2.txt
---------------------------------------------------------------------------------------------

paramspider:
paramspider -d example.com -o PS1.txt
---------------------------------------------------------------------------------------------

x8:
x8 -u "AliveSubs.txt" -o X81.txt
---------------------------------------------------------------------------------------------
-Merge URLs: cat WB1.txt GAU1.txt GAU2.txt KTN1.txt HK1.txt GS1.txt GS2.txt PS1.txt X81.txt | anew | tee AllURLs.txt

-Extract Interesting Data: cat AllURLs.txt | grep
                                              grep -i "\.js" > js.txt
                                              grep -i "\.asp" > asp.txt
                                              grep -i "\.php" > php.txt
                                              grep -i "\.jsp" > jsp.txt
                                              grep -i "\.jspx" > jspx.txt
                                              grep -i "\.aspx" > aspx.txt
                                              grep "=" > injection
------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

-Discover Interesting Points:

cat AllURLs.txt | urinteresting
------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

-Filter Live URLs:

cat AllURLs.txt | httpx -status-code -content-length -silent > LiveURLs.txt
------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

Extract Parameters

cat AllURLs.txt | grep "=" | qsreplace "FUZZ" | anew | tee ParamURLs.txt

cat AllURLs.txt | grep "=" | anew params.txt

cat AllURLs.txt | grep '=' | sed 's/=[^&]*/=/g' | tee param.txt
------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

JavaScript Discovery:  cat AllURLs.txt | grep -Ei "\.js(\?|$)" | anew js_urls.txt
                       cat AllURLs.txt | grep -iE '.js' | grep -ivE '.json' | sort -u | tee js.txt
                       https://web.archive.org/cdx/search/cdx?url=*.example.com/*&collapse=urlkey&output=text&fl=original&filter=original:.*.js$

API Discovery:         cat AllURLs.txt | grep -Ei "\.(json|xml|graphql|gql)(\?|$)" | anew api_urls.txt
Backend Files:         cat AllURLs.txt | grep -Ei "\.(php|asp|aspx|jsp|cfm|cgi)(\?|$)" | anew backend_files.txt
Login Flows:           cat AllURLs.txt | grep -Ei "login|signin|auth|oauth|reset|password" | anew login_flows.txt
Upload Endpoints:      cat AllURLs.txt | grep -Ei "upload|file|download|image|media" | anew file_uploads.txt
Admin Panels:          cat AllURLs.txt | grep -Ei "admin|dashboard|internal|manage" | anew admin_panels.txt
Sensitive Files:       cat AllURLs.txt | grep -Ei "\.(env|bak|config|sql|log)(\?|$)" | anew sensitive_files.txt
IDOR Targets:          cat AllURLs.txt | grep -Ei "[0-9]{2,}" | anew idor_targets.txt
Interesting Endpoints: cat AllURLs.txt | grep -Ei "admin|login|signup|redirect|callback|auth|dev|test|beta|debug|staging|url=|r=|u=|goto=|return=|dest=" | anew interesting.txt
Cloud Secrets:         cat AllURLs.txt | grep -Ei "aws|s3|bucket|gcp|azure|vault|token|apikey|secret" | anew cloud_leaks.txt
------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

JavaScript Secret Discovery:

cat AllURLs.txt | subjs
---------------------------------------------------------------------------------------------

cat js_urls.txt | mantra
---------------------------------------------------------------------------------------------

cat js_urls.txt | jsecret
---------------------------------------------------------------------------------------------

cat js_urls.txt | xargs -P 20 -I {} jsleak -s -l -k -e {} >> jsleak_output.txt
------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

Regex Secrets: grep -E "api[_-]?key|token|secret|password" file.js

------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

-Lazyegg:

python lazyegg.py http://example.com
python lazyegg.py http://example.com/js/auth.js
waybackurls vulnweb.com | grep '\.js$' | awk -F '?' '{print $1}' | sort -u | xargs -I{} bash -c 'python lazyegg.py "{}" --js_urls --domains --ips' > jsurls.log && cat jsurls.log | grep '\.' | sort -u

------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

-Secret Discovery:

trufflehog github --org=example-org --results=verified
trufflehog filesystem js_urls.txt --json > trufflehog_results.json
trufflehog git https://github.com/example/repo --results=verified
------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

-PHP Parameter Discovery:

arjun -i php_urls.txt >> php_parameters.txt
sqlmap -u "https://example.com/file.php?id=*" --dbs --banner --batch --random-agent
sqlmap -r sql.txt --dbs --banner --batch --random-agent
------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

-Full Vulnerability Scan:

nuclei -l all.txt -t /nuclei-templates/http/exposures -o results.txt
nuclei -u https://www.example.com -t /nuclei-templates/http/exposures

------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

-Hidden Parameters:

paraminer

arjun -i AllURLs.txt -o arjun.json

arjun -u https://example.com/test

arjun -u https://example.com/test -m post

ffuf -u http://example.com/search?FUZZ=value -w wordlist.txt
------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

-Port Discovery:

naabu:
naabu -list AliveSubs.txt -p - -rate 2000 -o ports.txt
---------------------------------------------------------------------------------------------
nmap:
nmap -iL AliveSubs.txt -T4 -Pn
------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

-Advanced Wayback Sensitive File Enumerator:

waybackurls https://www.hackerone.com | grep --color=always -E "\.xls|\.xlsx|\.csv|\.sql|\.db|\.bak|\.backup|\.old|\.tar\.gz|\.tgz|\.zip|\.7z|\.rar|\.pdf|\.doc|\.docx|\.pptx|\.txt|\.log|\.ini|\.conf|\.config|\.env|\.json|\.xml|\.yml|\.yaml|\.pem|\.key|\.crt|\.ssh|\.git|\.htaccess|\.htpasswd|\.php|\.swp|\.swo|\.dump|\.dmp|\.ds_store|\.env\.local|\.env\.prod|\.env\.dev|\.env\.test|\.env\.example|\.env\.sample|\.env\.development|\.env\.production|\.env\.staging|\.env\.backup|\.env\.old|\.env\.save|\.env\.tmp|\.env\.temp|\.env\.log|\.env\.json|\.env\.yaml|\.env\.xml|\.env\.conf|\.env\.cfg|\.env\.settings|\.env\.secret|\.env\.keys|\.env\.credentials|\.env\.tokens|\.env\.api|\.env\.database|\.env\.mysql|\.env\.postgres|\.env\.redis|\.env\.mongo|\.env\.aws|\.env\.s3|\.env\.gcp|\.env\.azure|\.env\.docker|\.env\.k8s|\.env\.vault|\.vscode|\.idea|\.DS_Store|\.gitignore|\.gitconfig|\.gitmodules|\.gitattributes|\.gitkeep|\.gitlab-ci\.yml|\.travis\.yml|\.circleci|\.dockerignore|\.dockerfile|\.docker-compose\.yml|\.npmrc|\.yarnrc|\.bowerrc|\.eslintrc|\.eslintignore|\.prettierrc|\.prettierignore|\.stylelintrc|\.stylelintignore|\.htgroup|\.htusers|\.htdigest|\.htdbm|\.htpasswds|\.htaccess\.bak|\.htaccess\.old|\.htaccess\.backup|\.htaccess\.save|\.htaccess\.tmp|\.htaccess\.temp|\.htaccess\.log|\.htaccess\.json|\.htaccess\.yaml|\.htaccess\.xml|\.htaccess\.conf|\.htaccess\.cfg|\.htaccess\.settings|\.htaccess\.secret"
------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

-Sensitive Data Leaks Using Google Sheets:

site:*.target.com intext:"docs.google.com/spreadsheets"
site:docs.google.com/spreadsheets "target.com"
site:docs.google.com/spreadsheets "password" "test.com"
site:docs.google.com/spreadsheets "@test.com"
------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

-GitHub dorks:

python3 GitDorker.py -tf tf/TOKENSFILE -q example.com -d dorks/medium_dorks.txt -o example
---------------------------------------------------------------------------------------------
https://github.com/Proviesec/github-dorks
https://mr-koanti.github.io/github.html
------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

-Backup File Artifacts Checker:

bfac --url https://example.com --detection-technique all --level 3 --exclude-status-codes 404,500
------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

What is Origin IP?

Origin IP = the real server IP behind a website.

Example:
example.com â†’ 104.x.x.x (Cloudflare IP)
example.com â†’ 192.x.x.x (Origin IP - real server)

Tools:

https://github.com/rix4uni/originiphunter --> nano ~/.config/originiphunter/config.yaml
                                              echo "example.com" | originiphunter
                                              cat domains.txt | originiphunter
------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
-Directory Fuzzing:

dirb https://example.com
---------------------------------------------------------------------------------------------
feroxbuster -u https://example.com -w wordlist.txt -t 300 -k -d 3 -e -x php,html,json,js,log,txt,bak,old,zip,tar,gz
---------------------------------------------------------------------------------------------
gobuster dir -u https://example.com -w wordlist.txt -k
------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

-Directory Scanning:

dirsearch: python3 dirsearch.py -u https://example.com -i 200 --full-url -o result.txt
           python3 dirsearch.py -u https://example.com-i 200 --recursive
           python3 dirsearch.py -u https://example.com --random-agent --full-url --deep-recursive
           python3 dirsearch.py -u https://example.com -m post
           python3 dirsearch.py -u https://example.com --extensions=php,asp,aspx,jsp,json,xml,txt,log,ini,cfg,config,conf,bak,old,backup,zip,tar,tgz,gz,rar,7z,swp,swo,db,sql
           python3 dirsearch.py -u https://example.com --include-status=200,204,301,302,307,308,401,403  --exclude-status=404
           python3 dirsearch.py -u https://example.com -w wordlist.txt -w wordlist.txt -e php,asp,aspx,jsp,json,xml,txt,log,ini,cfg,config,conf,bak,old,backup,zip,tar,tgz,gz,rar,7z,swp,swo -t 80  -r  --full-url --min-response-size 1 -i 200,204,301,302,307,308,401,403 -x 404,500,501,502,503,504 -O plain -o dirsearch_sensitive.txt -m POST
           python3 dirsearch.py -u https://example.com -r -R 3 -e php,html,js,json,txt,bak,zip,tar,gz,old,backup,conf
------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

-Advanced FFUF:

ffuf: ffuf -u https://example.com/FUZZ -w wordlist.txt -t 2000  -mc 200
      ffuf -u https://example.com:80/FUZZ -w wordlist.txt -X POST
      ffuf -u https://192.1.2.3:80/FUZZ -w wordlist.txt
      ffuf -u https://example.com/FUZZ/FUZZX  -w list1.txt:FUZZ  -w list2.txt:FUZZX
      ffuf -u https://example.com/FUZZ -w wordlist.txt -H "X-Forwarded-For:127.0.0.1" -H "X-Forwarded-Host:127.0.0.1" (bypass ratelimit)
      ffuf -u http://example.com/FUZZ -w wordlist.txt -e .html,.php,.asp,.aspx,.js,.json,.xml,.config,.bak,.old,.backup,.zip,.rar
      ffuf -u http://example.com/FUZZ -w wordlist.txt -H Authorization: Bearer TOKEN
      ffuf -u http://example.com/FUZZ -w wordlist.txt -recursion
      ffuf -u http://example.com/FUZZ -w wordlist.txt -recursion-depth
      ffuf -u http://example.com/FUZZ -w wordlist.txt -x http://127.0.0.1:8080 (proxy use)
      ffuf -u https://example.com/?username=FUZZ&password=FUZZX  -w username.txt:FUZZ -w password.txt:FUZZX
      ffuf -request fuzzing_login.txt -request-proto http -w password.txt:PASS
      ffuf -u https://example.com/FUZZ?param=FUZZX -w dirs.txt:FUZZ -w params.txt:FUZZX
      ffuf -u https://example.com/admin -w 403-headers.txt -H "FUZZ" -mc 200,301,302,307,401 --> https://github.com/Karanxa/Bug-Bounty-Wordlists/blob/main/403_header_payloads.txt
      ffuf -u https://example.com/FUZZ -w wordlist.txt  -H "X-Forwarded-For: 127.0.0.1"  -H "X-Original-URL: /FUZZ" (403 bypass)
------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

-Directory&Parameter Wordlists:

/usr/share/wordlists/seclists/Discovery/Web-Content/raft-large-directories.txt
/usr/share/wordlists/seclists/Discovery/Web-Content/raft-large-files.txt
/usr/share/wordlists/seclists/Discovery/Web-Content/common.txt
/usr/share/wordlists/seclists/Discovery/Web-Content/directory-list-2.3-medium.txt
/usr/share/wordlists/seclists/Discovery/Web-Content/raft-medium-directories.txt
/usr/share/wordlists/seclists/Discovery/Web-Content/raft-medium-files.txt
/usr/share/wordlists/seclists/Discovery/Web-Content/burp-parameter-names.txt
------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

-API Endpoint Discovery & Fuzzing:

kiterunner: kr wordlist list
            kr scan https://api.example.com -A=apiroutes-260227:10000 -x 8 -j 15 -v info  (/api/v1)
            kr scan https://api.example.com.com -A=parameters-260227:5000 -x 5 -j 10 -v info  (/api/users?user_id=1)
            kr scan https://api.example.com.com -A=directories-260227:8000 -x 6 -j 12 -v info (/uploads)
            kr scan targets.txt -A=directories-260227:8000 -x 6 -j 12 -v info
            kr scan https://api.example.com.com -w wordlist.txt -H 'x-access-token:123'

kr Wordlists:

kr wordlist save 2m-subdomains
kr wordlist save asp_lowercase
kr wordlist save aspx_lowercase
kr wordlist save bak
kr wordlist save best-dns-wordlist
kr wordlist save cfm
kr wordlist save do
kr wordlist save dot_filenames
kr wordlist save html
kr wordlist save apiroutes-251027
kr wordlist save aspx-251027
kr wordlist save cgi-251027
kr wordlist save directories-251027
kr wordlist save html-251027
kr wordlist save js-251027
kr wordlist save jsp-251027
kr wordlist save parameters-251027
kr wordlist save php-251027
kr wordlist save subdomains-251027
kr wordlist save txt-251027
kr wordlist save xml-251027
kr wordlist save jsp
kr wordlist save php
kr wordlist save phpmillion
kr wordlist save pl
kr wordlist save raft-large-directories-lowercase
kr wordlist save raft-large-directories
kr wordlist save raft-large-extensions-lowercase
kr wordlist save raft-large-extensions
kr wordlist save raft-large-files-lowercase
kr wordlist save raft-large-files
kr wordlist save raft-large-words-ext
kr wordlist save raft-large-words-lowercase
kr wordlist save raft-large-words
kr wordlist save raft-medium-directories-lowercase
kr wordlist save raft-medium-directories
kr wordlist save raft-medium-extensions-lowercase
kr wordlist save raft-medium-extensions
kr wordlist save raft-medium-files-lowercase
kr wordlist save raft-medium-files
kr wordlist save raft-medium-words-lowercase
kr wordlist save raft-medium-words
kr wordlist save raft-small-directories-lowercase
kr wordlist save raft-small-directories
kr wordlist save raft-small-extensions-lowercase
kr wordlist save raft-small-extensions
kr wordlist save raft-small-files-lowercase
kr wordlist save raft-small-files
kr wordlist save raft-small-words-lowercase
kr wordlist save raft-small-words
kr wordlist save wordlist_no_underscores
kr wordlist save wordlist_with_underscores
kr wordlist save xml_filenames