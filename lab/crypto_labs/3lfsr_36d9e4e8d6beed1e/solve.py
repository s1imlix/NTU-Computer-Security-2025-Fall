from tqdm import tqdm
import random

poly1 = [0, 2, 11, 21, 23]
poly2 = [0, 1, 61, 114, 519]
poly3 = [0, 13, 37, 68, 87]

class LFSR:
    def __init__(self, poly: list[int], state: int):
        # the characteristic polynomial is exactly sum(x**e for e in poly)
        self._tap = poly[:-1]
        self._state = state
        self._shift = poly[-1] - 1
        self._mask = sum([1 << i for i in self._tap])

    def __call__(self):
        f = 0
        for i in self._tap:
            f ^= (self._state >> i) & 1
        x = self._state & 1
        self._state = (self._state >> 1) | (f << self._shift)
        return x

    @staticmethod
    def fixed_with_poly(poly: list[int], state: int):
        return LFSR(poly, state)


def randbyte(rng: LFSR):
    byte = 0
    for _ in range(8):
        byte = (byte << 1) | rng()
    return byte


def lfsr_expr(a, b, c):
    return (3*a + 5*b + 7*c) % 11 % 2

def truth_table():
    match = [0] * 3
    for i in range(2**3):
        a = (i >> 2) & 1
        b = (i >> 1) & 1
        c = i & 1
        result = lfsr_expr(a, b, c)
        print(f"a={a}, b={b}, c={c} => result={result}")
        for j in range(3):
            if (i >> (2 - j)) & 1 == result:
                match[j] += 1
    print(f"rng1 match {match[0]}/8, rng2 match {match[1]}/8, rng3 match {match[2]}/8")


import math 

alpha = 1e-3
beta = 1e-3

def crack_rng(keystream, poly, p1, p0):
    # one state produces matches 75% of the time
    best_state = None
    best_diff = 1e8
    llr_match = math.log(p1 / p0)
    llr_nomatch = math.log((1 - p1) / (1 - p0))
    # A = math.log((1 - beta) / alpha)
    B = math.log(beta / (1 - alpha))
    keystream = [(b >> i) & 1 for b in keystream for i in reversed(range(8))]
    assert len(keystream) == 512 * 8
    n = len(keystream)
    print(f'B={B}, llr_match={llr_match}, llr_nomatch={llr_nomatch}')
    for state in tqdm(range(2**poly[-1])):
        lfsr = LFSR.fixed_with_poly(poly, state)
        match = 0
        llr = 0.0
        for i in range(n):
            # invert lfsr output
            out = lfsr() 
            if out == keystream[i]:
                match += 1
                llr += llr_match
            else:
                llr += llr_nomatch 
            if llr < B:
                break
        diff = abs(match - p1 * n)
        if diff < best_diff and llr >= B:
            print(f"new best state {state:#0{8}x} with match {match}/{n} and diff {diff}")
            best_diff = diff
            best_state = state
    print(f"best state for rng: {best_state:#0{8}x} with diff {best_diff}")
    return best_state
        
def remove_rng1(keystream, rng_state):
    lfsr = LFSR.fixed_with_poly(poly1, rng_state)
    keystream = [(b >> i) & 1 for b in keystream for i in reversed(range(8))]
    n = len(keystream)
    updated_keystream = []
    # compute (5*b + 7*c) % 11 % 2 
    # ignore %2, 3*a % 11 + (5*b + 7*c) % 11 == (3*a + 5*b + 7*c) % 11
    # given their parity, xor to get the third parity 
    for i in range(n):
        out = (3 * lfsr()) % 11 % 2
        updated_bit = (keystream[i] ^ out)
        updated_keystream.append(updated_bit)
    # convert back to bytes
    updated_keystream_bytes = bytearray()
    for i in range(0, n, 8):
        byte = 0
        for j in range(8):
            byte = (byte << 1) | updated_keystream[i + j]
        updated_keystream_bytes.append(byte)
    return bytes(updated_keystream_bytes)

if __name__ == "__main__":
    truth_table()
    enc_flag = b""
    keystream = b""
    with open("./output.txt", "r") as f:
        b = bytes.fromhex(f.read())
        # last 512 bytes are keystream
        enc_flag, keystream = b[:-512], b[-512:]
    # testing with custom state

    rng1_state = 0x0f29e8
    # update keystream by removing rng1
    # updated_keystream = remove_rng1(keystream, rng1_state)
    # crack_rng(updated_keystream, poly3, 0.75, 0.5)
    
        
