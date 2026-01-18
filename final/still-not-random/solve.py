import hmac
import math
from hashlib import sha256
from fastecdsa.curve import P384
from Crypto.Cipher import AES
from sage.all import *

sigs = [(317707421133410288073354603009480426136391906002873302709570879761947103070512898051132583840618463139472027601216698251294206460344755339051109898589809987983731707077909099505833365567522347006453766545663380230105595126817790425, 25185752159924706126981435669717936861361993674900106138337831137838509453749313533989197233649309651483579988978205), (417548456675579988606680466439690234874946492911623920447331037240230655879606626325624623314611471522814787475988129078726743347417903386362824681134780863810523742180718053363084828145812067731683272119151061828749117659255650820, 27618563118772187320593702066291845973666620541831283288991142064228070314197536489147588491763843793593821643513457), (703771273054730080235579285501232710659154148145979519264450072512823561624248636822569827736905476306443746390214567198923437156846958456303186787370323078966806939434118158768394748234214487029382926999880135374613932395712372460, 27052092405825396792237011211691900251888872753276208811631357208317438773416505653305767076226992282260977625878007), (821717323558426535455119744526279609022144869806906586662554363968363839151910768914318502227461974453838258550953434850776924606792184210954238562503515009237179979646111655773804054528212491391076376250546737439142144165942539844, 28870411728276849847003745583242490365442899058004875752358198407125701328587711166784961247940279464305857022011977)]
ct = b'iXm\x982\xc5\xf23\x85\x88\x91\x0c\x7f\xdc\x1b,\x1b\x82\x9d\xcd\x00 BWn\xad\n\xc3`\xe7\x8e\xfc`%\x9cQ\x12E\x97\x97\xa5\xd5t\x8b\x87v\xb4\xcf\x8d'

dim = len(sigs) + 2
q = P384.q

msgs = [
    b"https://www.youtube.com/watch?v=LaX6EIkk_pQ",
    b"https://www.youtube.com/watch?v=wK4wA0aKvg8",
    b"https://www.youtube.com/watch?v=iq90nHs3Gbs",
    b"https://www.youtube.com/watch?v=zTKADhU__sw",
]


def p2i(P) -> int:
    return P.x * P.curve.p + P.y

def decrypt_flag(sk, ciphertext):
    try:
        key = int(sk & ((1 << 128) - 1)).to_bytes(16)
        
        nonce = ciphertext[:8]
        encrypted_payload = ciphertext[8:]
        
        cipher = AES.new(key, AES.MODE_CTR, nonce=nonce)
        plaintext = cipher.decrypt(encrypted_payload)
        
        print(f"Decrypted: {plaintext}")
        
        if b'EOF{' in plaintext:
            print("\n[+] SUCCESS! Flag found.")
        else:
            print("\n[-] output doesn't look like a flag. Check byteorder or SK.")

    except Exception as e:
        print(f"Error: {e}")

def center(x, q):
    x = ZZ(x)
    x %= q
    if x > q//2:
        x -= q
    return x

def check_sk_by_signatures(sk: int) -> bool:
    # Strong check: k = s - sk*e (mod q), then p2i(kG) == r
    for (r, s), msg in zip(sigs, msgs):
        e = compute_e(r, msg)
        k = (int(s) - (int(sk) * int(e))) % q
        if p2i(k * P384.G) != int(r):
            return False
    return True

def compute_e(r: int, msg: bytes) -> int:
    rb = int(r).to_bytes(1337, "big")
    return int.from_bytes(hmac.new(rb, msg, sha256).digest(), "big") % q


"""
HNP with shared MSB
k_i = 2^256 * K + h_i, K = int(sha256(sk))
s_i = k_i + sk * e_i mod q
s_i = (2^256 * sk + h_i + sk * e_i) mod q
   s_i - 2^256 * sk - h_i - sk * e_i = 0 mod q
-) s_j - 2^256 * sk - h_j - sk * e_j = 0 mod q
=> (s_i - s_j) - sk * (e_i - e_j) - (h_i - h_j) = 0 mod q    
Fix j = 1              
beta_i = s_i - s_1, ti = e_i - e_1, ai = h_i - h_1
"""

r0, s0 = sigs[0]
e0 = compute_e(r0, msgs[0])

ai_vals = [] # ai
ti_vals = [] # ti

for i in range(1, len(sigs)):
    ri, si = sigs[i]
    ei = compute_e(ri, msgs[i])
    # ai = (si - s0) % q
    # ti = (ei - e0) % q
    ai_vals.append(center(int(s0) - int(si), q))
    ti_vals.append(center(int(e0) - int(ei), q))

"""
We scale all rows by q so they're all integer
B = 
[
    q^2   0     ...   0   0   0
    0   q^2     ...   0   0   0
    ...
    0   0       ... q^2   0   0
    q*t1  q*t2  ... q*tn  B   0
    q*a1  q*a2  ... q*an  0   B*q
]
LLL[0] = (-t1, -t2, ..., q, 0) = [0, 0, ... B*q, 0]
LLL[1] = (k_1, ..., k_n, sk, -1) = [qbeta_1, ..., qbeta_n, B*sk, -B*q] <- look for B*q
"""

B = 2**256  
n = len(ai_vals)
dim = n + 2 
M = matrix(ZZ, dim, dim)

for i in range(n):
    M[i, i] = q * q

for i in range(n):
    M[n, i] = ti_vals[i] * q
M[n, n] = B

for i in range(n):
    M[n+1, i] = ai_vals[i] * q
M[n+1, n+1] = q * B
print("[+] Reducing lattice...")

L = M.LLL()
rows = list(L.rows())
print(f"[+] Got {len(rows)} reduced rows")
cand_rows = [ r for r in rows if abs(int(r[n+1])) == B*q ]
print(f"[+] Found {len(cand_rows)} candidate rows with last coord ±B*q")

for idx, row in enumerate(cand_rows):
    skB = int(row[n])
    for sign in (+1, -1):
        sk_cand = sign * (skB // B) % q
        for delta in (0, 1, -1, 2, -2, 3, -3):
            print(f"row={idx}, sign={sign}, delta={delta}")
            sk = (sk_cand + delta) % q
            if check_sk_by_signatures(sk):
                print(f"[+] Found valid SK: {sk}")
                decrypt_flag(sk, ct)
                break
            


