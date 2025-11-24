#!/bin/bash

# Check if URL is provided
if [ $# -eq 0 ]; then
    echo "Usage: $0 <favicon_url>"
    echo "Example: $0 https://cybersecurity.wtf/favicon.ico"
    exit 1
fi

URL="$1"

# Get favicon and calculate mmh3 hash
hash=$(curl -s "$URL" | base64 | python3 -c "
import mmh3
import sys

favicon_b64 = sys.stdin.read()
print(mmh3.hash(favicon_b64))
")

echo "$hash"
