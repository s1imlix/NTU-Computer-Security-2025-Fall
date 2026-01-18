from pwn import *
from hashlib import sha256
from math import gcd

from sage.all import *

from ecdsa.curves import SECP256k1
from ecdsa.ellipticcurve import Point

import time

"""
smol fan is almost identical to huuge fan 
you just have to get the (r,s) pairs yourself
"""

HOST = "smol.chalz.nitectf25.live"
PORT = 1337

FLAG_MESSAGE = b"gimme_flag"
K_BOUND = 2**200
TEN_POW_11 = 10**11

curve = SECP256k1.curve
G = SECP256k1.generator
n = SECP256k1.order

def recv_menu(p):
    p.recvuntil(b"Menu:")
    p.recvuntil(b"> ")

def get_pubkey(p):
    p.sendline(b"1")
    p.recvuntil(b"Qx = ")
    qx = int(p.recvline().strip())
    p.recvuntil(b"Qy = ")
    qy = int(p.recvline().strip())
    p.recvuntil(b"> ")
    return qx, qy

def sign_oracle(p, msg: bytes):
    p.sendline(b"2")
    p.recvuntil(b"Enter message as hex: ")
    p.sendline(msg.hex().encode())

    p.recvuntil(b"m = ")
    m = int(p.recvline().strip())

    p.recvuntil(b"a = ")
    a = int(p.recvline().strip())
    # blank line due to f-string "\n"
    p.recvline()

    p.recvuntil(b"b = ")
    b = int(p.recvline().strip())
    p.recvline()

    p.recvuntil(b"> ")
    return m, a, b


def ecdsa_verify_with_pubkey(qx: int, qy: int, msg: bytes, r: int, s: int) -> bool:
    if not (1 <= r < n and 1 <= s < n):
        return False
    z = int.from_bytes(sha256(msg).digest(), "big") % n
    w = pow(s, -1, n)
    u1 = (z * w) % n
    u2 = (r * w) % n
    Q = Point(curve, qx, qy, n)
    X = u1 * G + u2 * Q
    return (X.x() % n) == r

"""
one small thing here is that server gives us m, a, b instead of r,s
but we can recover it

m =  r*s
a = pow(10 + r, 11, m)
b = pow(s^2 + 10, r, m)
a = 10^11 mod r, kr = a - 10^11
r = gcd(m, a - 10^11), s = m // r
"""

def recover_rs_from_ma(qx: int, qy: int, msg: bytes, m: int, a: int):
    g = gcd(m, a - TEN_POW_11)
    if g == 1 or g == m:
        raise ValueError("gcd trick failed; try another signature")
    r1, s1 = g, m // g

    if ecdsa_verify_with_pubkey(qx, qy, msg, r1, s1):
        return r1, s1
    if ecdsa_verify_with_pubkey(qx, qy, msg, s1, r1):
        return s1, r1

    raise ValueError("Recovered factors but neither ordering verifies; try another signature")


def recover_d_via_lll(ts, us):
    """
    B = 
    [
        q   0   ... 0   0   0
        0   q   ... 0   0   0
        ...
        0   0   ... q   0   0
        B1  B2  ... Bn  W/q 0
        A1  A2 ...  An  0   W
    ]
    again scale rows to avoid float 
    """
    m = len(ts)
    B = matrix(ZZ, m + 2, m + 2)
    SCALE = n // K_BOUND
    for i in range(m):
        B[i, i] = n * SCALE 
        B[m, i] = int(ts[i]) * SCALE
        B[m + 1, i] = int(us[i]) * SCALE
    B[m, m] = 1
    B[m + 1, m + 1] = n

    L = B.LLL()
    print(L[0], L[1])
    d = L[1][-2] % n

    return d


def forge_signature(d: int, msg: bytes):
    z = int.from_bytes(sha256(msg).digest(), "big") % n
    while True:
        k = ZZ.random_element(1, n)
        R = int(k) * G
        r = R.x() % n
        if r == 0:
            continue
        s = (pow(int(k), -1, n) * (z + r * d)) % n
        if s == 0:
            continue
        return int(r), int(s)


def main():
    p = remote(HOST, PORT, ssl=True)
    recv_menu(p)

    qx, qy = get_pubkey(p)
    info(f"Qx={qx}")
    info(f"Qy={qy}")

    rs = []
    ts = []
    us = []

    NUM_TRIES = 5 # should be enough

    i = 0
    info("Starting signature collection...")
    while True:
        msg = b"msg_" + str(i).encode()
        i += 1

        info(f"collecting signature (r,s) #{i}...")
        m, a, _b = sign_oracle(p, msg)
        try:
            r, s = recover_rs_from_ma(qx, qy, msg, m, a)
        except Exception:
            continue

        info(f"recovered (r,s)=({r},{s}) from (m,a)=({m},{a})")

        z = int.from_bytes(sha256(msg).digest(), "big") % n
        inv_s = pow(s, -1, n)
        t = (r * inv_s) % n
        u = (z * inv_s) % n

        rs.append((r, s))
        ts.append(t)
        us.append(u)

        info(f"got sig {len(rs)}")

        if len(rs) < NUM_TRIES:
            continue

        try:
            d = recover_d_via_lll(ts, us)
            info(f"recovered d = {d}")
            break
        except Exception as e:
            print(f"[-] lattice not ready yet: {e}")
            if len(rs) >= 30:
                raise

    r_flag, s_flag = forge_signature(d, FLAG_MESSAGE)
    print(f"[+] forged r={r_flag}")
    print(f"[+] forged s={s_flag}")

    p.sendline(b"3")
    p.recvuntil(b"Enter r: ")
    p.sendline(str(r_flag).encode())
    p.recvuntil(b"Enter s: ")
    p.sendline(str(s_flag).encode())

    out = p.recvline(timeout=5)
    if out:
        print(out.decode())

if __name__ == "__main__":
    main()


