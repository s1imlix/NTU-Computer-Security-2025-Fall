import hmac
import math
from hashlib import sha256
from fastecdsa.curve import P384
from fastecdsa.keys import gen_keypair
from Crypto.Cipher import AES
from fastecdsa.ecdsa import sign
from sage.all import *

sigs = [(439466984244556297836955027962075494068111897267493274652013936909865855963925172887770398609453822698046470141968, 12688214135249352463448347907973349419434869788829072791318493259402827088612671955967108221849081200403097252113952), (5213132559509325630360067691624138030043889782236709042506945661619145303705979952137555908359307570344902332623814, 34913789473835125515865536615500951595689820825465574424919323137533074749513972075124212989224159874275538713053313), (16837774656865790250525711083651320547412706513406518515115905509572913267046579547895420452500864437009493477780094, 20029939263395674736349579264090235514607748285299378154193414785894784684485857586294281789663330285135172860084016), (32949775214749405338348840756175978687084842150217194208919294140991271135711416322597818131090445944238069986255221, 17941995812490591927576124175281036781859780405720340499139578554610923582590340653528314389779038549773488871739406)]
ct = b'\xb4\x1ej\xf7\xfd\x92.\xc2\xa6\xb4\xce\xac6\x00p\t\xe5[\xf1\x81\xd8gK\x01\x83\x9cl\x12\xa7G\x1a\x8c\x1d\x05\xb8\xb7b\xfd\x04\xcb\x01\xc3\xe0ze\xe0\x1d\x17\xd4\x00B\x83\xbe\xb5r\x1a#\xf5T\x93\xa5'

dim = len(sigs) + 2
q = P384.q

msgs = [
    b"https://www.youtube.com/watch?v=3RuCaE5ciNU",
    b"https://www.youtube.com/watch?v=t0xj5ZxWU3c",
    b"https://www.youtube.com/watch?v=lpPih3tTuM0",
    b"https://www.youtube.com/watch?v=RR0gRA0vhrI",
]

def decrypt_flag(sk, ciphertext):
    try:
        mask_128 = (1 << 128) - 1
        key_int = sk & mask_128
        
        key = key_int.to_bytes(16, 'big')
        
        nonce = ciphertext[:8]
        encrypted_payload = ciphertext[8:]
        
        cipher = AES.new(key, AES.MODE_CTR, nonce=nonce)
        plaintext = cipher.decrypt(encrypted_payload)
        
        print(f"Decrypted: {plaintext}")
        
        if b'flag{' in plaintext.lower():
            print("\n[+] SUCCESS! Flag found.")
        else:
            print("\n[-] output doesn't look like a flag. Check byteorder or SK.")

    except Exception as e:
        print(f"Error: {e}")

"""
Hidden number problem: k = hash(sk, msg)
s = k^-1 (z + r*sk) mod q
s*k = z + r*sk mod q 
k = s^-1*z + s^-1*r*sk mod q, B = r*s^-1, A = s^-1*z
=> k - B * sk - A = 0 mod q
=> k = B * sk + A + m*q

(https://eprint.iacr.org/2023/032.pdf, p21)
beta_i = k_i, t_i = B_i, alpha = sk, a_i = A_i
can ignore A's sign 

W < k for any k, so W = 2^256 since it is sha256
B = 
[
    q   0   ... 0   0   0
    0   q   ... 0   0   0
    ...
    0   0   ... q   0   0
    B1  B2  ... Bn  W/q 0
    A1  A2 ...  An  0   W
]

u' = (m_1, ..., m_n, sk, 1) 
   = [m_1*q + sk * B_i + A_i, ..., sk * W / q, - W]
   = [k_1, k_2, ..., k_n, sk * W / q, - W]

[0, 0, ... W, 0] = (-B_1, -B_2, ..., -B_n, q, 0), so use LLL[1]
"""

n = len(msgs)
    
A_vals = [] 
B_vals = [] 

for i, msg in enumerate(msgs):
    r, s = sigs[i]
    z = int.from_bytes(sha256(msg).digest(), 'big')
    s_inv = pow(s, -1, q)
    A = (s_inv * z) % q
    B = (s_inv * r) % q
    A_vals.append(A)
    B_vals.append(B)

"""
We scale all rows by q/W = SCALE so they're all integer
B = 
[
    qS   0   ... 0   0   0
    0   qS   ... 0   0   0
    ...
    0   0     ... qS   0   0
    SB1  SB2  ... SBn  1   0
    SA1  SA2  ... SAn  0   q
]
LLL[0] = (-B1, -B2, ..., q, 0) = [0, 0, ... q, 0]
LLL[1] = (m_1, ..., m_n, sk, 1) = [Sk_1, ..., Sk_n, sk, q]
"""


SCALE = 2**128  
dim = n + 2
M = matrix(ZZ, dim, dim)

for i in range(n):
    M[i, i] = q * SCALE

for i in range(n):
    M[n, i] = B_vals[i] * SCALE
M[n, n] = 1 

for i in range(n):
    M[n+1, i] = A_vals[i] * SCALE
M[n+1, n+1] = q 

# 3. Reduce
print("Reducing lattice...")
L = M.LLL()
print(L[0], L[1])
sk = L[1][-2] % q
print(f"sk = {sk}")
decrypt_flag(sk, ct)
