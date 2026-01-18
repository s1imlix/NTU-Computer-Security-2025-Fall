from sage.all import *
from Crypto.Util.number import long_to_bytes
import ast
from hashlib import sha256
import math

"""
TL;DR: HNP with Known MSB in nonce
Please refer to "Hidden Number Problem" and how to formulate Known MSB into HNP
in the following document => https://eprint.iacr.org/2023/032.pdf
"""

"""
Some constants
"""
m = 2**446 - 0x8335DC163BB124B65129C96FDE933D8D723A70AADC873D6D54A7BB0D
R = Zmod(m)
q = int(str(m)[:4])              
L = len(str(m))
data = ast.literal_eval(open("out.txt", "r").read())   # list[(n, signs)]
W = 10 ** (L-4)

"""
Each "recording" was a group of 5 signatures + n derived from the nonces
let the nonces be k1, k2, k3, k4, k5
(1) ki' = str(int(ki))[:4] mod q i.e. it's the first 4 decimal digits of ki
(2) define A = 1*k1' + q* k2' + q^2 * k3' + q^3 * k4' + q^4 * k5'
           B = q^4 * k1' + q^3 * k2' + q^2 * k3' + q * k4' + 1 * k5'
(3) n = A * B, i.e. it's the qnary representation & its reverse times together

(2,3) can be reversed so from n, we can recover k1', k2', k3', k4', k5' 
(1) is unknown by a factor of q, so for some ti, ni
ki = 10^{L - 4} * (ki' + niq) + ti
"""

def baseq_digits_5(x):
    x = ZZ(x)
    ds = []
    for _ in range(5):
        ds.append(int(x % q))  
        x //= q
    return ds                  

def reverse_from_digits_5(ds):
    return sum(ZZ(ds[4-i]) * (ZZ(q)**i) for i in range(5))

def recover_parts_mod_q(n):
    n = ZZ(n)
    for Bcand in n.divisors():              
        ds = baseq_digits_5(Bcand)
        if reverse_from_digits_5(ds) * Bcand == n:
            return ds                      
    raise ValueError("no base-q reversal factor found")

def hashmsg(msg: bytes):
    return R(int.from_bytes(sha256(msg).digest()))

"""
This problem is similar to known MSB just with a base-10 leak
let L = len(str(int(m))), q = int(str(int(m))[:4])
remember: ki = 10^{L - 4} * (ki' + niq) + ti
plugging that into signature equation:

siki = zi + rid mod m
=> si(10^{L - 4} * (ki' + niq) + ti) = zi + rid mod m
=> (ti + 10^{L - 4} * niq) 
   - si^{-1}ri * d 
   + (10^{L - 4} * ki' - si^{-1} * zi) = Ki * m
=> HNP with βi, ti = si^{-1} * ri, ai = (10^{L - 4} * ki' - si^{-1} * zi)
where ti, ai are known and βi = ki - 10^{L - 4} * ki' < m 
"""


"""
Prepare HNP parameters
"""
t_i = []
a_i = []

for (n, signs) in data:
    parts = recover_parts_mod_q(n)   # these ARE the exact 4-digit prefixes
    if parts != sorted(parts):
        parts = parts[::-1] # ensure sorted order
    for j, (msg_hex, r, s) in enumerate(signs):
        if parts[j] == 0:
            continue
        msg = bytes.fromhex(msg_hex)
        z = hashmsg(msg)

        r = R(r)
        s = R(s)
        s_inv = inverse_mod(s, m)

        t = s_inv * r
        a = parts[j] * W - s_inv * z

        t_i.append(int(t))
        a_i.append(int(a))

"""
I use the setup factor c = ceil(m / W) so that the matrix is in ZZ
B =
[
    m*c    0     ...   0      0      0
    0     m*c    ...   0      0      0
    ...
    0      0     ...  m*c     0      0 
    t1*c  t2*c   ...  tN*c    1      0
    a1*c  a2*c   ...  aN*c    0      m*c
]
with (K1, K2, ..., KN, d, -1) generating (cβ1, cβ2, ..., cβN, d, -c*m)
since we have (t1, t2, ..., tN, m, 0) generating (0, 0, ..., 0, m, 0)
it will not be the shortest vector in LLL-reduced basis
βi is only slightly less (<m is a loose bound) than m... but enough
"""

N = len(t_i)
c = (m + W - 1) // W  # ceil(m / W) 
B = m                  
M = Matrix(ZZ, N+2, N+2)

for i in range(N):
    M[i, i] = m * c

for i in range(N):
    M[N, i] = t_i[i] * c
M[N, N] = 1

for i in range(N):
    M[N+1, i] = a_i[i] * c
M[N+1, N+1] = B * c

Mred = M.LLL()

#search for the target vector
for row in Mred.rows():
    if abs(row[N+1]) != B * c:
        continue
    sgn = 1 if row[N+1] == -B * c else -1 # flip sign if necessary
    d_candidate = (sgn * row[N]) % m

    ok = True # sanity check if it is (cbeta_1, ..., cbeta_N, d, -B)
    for i in range(N):
        if row[i] % c != 0:
            ok = False; break
        beta = sgn * (row[i] // c)
        if abs(beta) >= W:
            ok = False; break
        if (t_i[i] * d_candidate - a_i[i] - beta) % m != 0:
            ok = False; break

    print("target row:", row)
    if ok:
        print("FOUND d =", d_candidate)
        print("FLAG:", long_to_bytes(d_candidate))
        break