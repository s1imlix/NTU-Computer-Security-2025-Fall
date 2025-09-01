import os 
import sys 
from sympy.ntheory.modular import crt
from Crypto.Util.number import long_to_bytes, sieve_base
from functools import reduce 

OUTPUT_DIR = "./output/"
primes = [p for p in sieve_base if p.bit_length() == 12]

def get_msg_len(data):
    # find which prime divides len(data) 
    data_len = len(data)
    for p in primes:
        if data_len % p == 0:
            return data_len // p
    raise ValueError("No prime found that divides data length")

def update_by_bytes(freqs, bytes):
    for byte in bytes:
        for i in range(8):
            if (byte >> (7 - i)) & 1:
                freqs[i] += 2
            else:
                freqs[i] += 1


def estimate_and_guess(data, msg_len):
    """
    For given message, given K is random key, assume 0/1 equally likely
    if M[i] == 1: -> 2/3 being 1
        xor: 1/2, 1/2
        and: 1/2, 1/2
        or: 1
    if M[i] == 0: -> -> 1/3 being 1
        xor: 1/2, 1/2
        and: 0
        or: 1/2, 1/2
    """
    msg_repeat_count = len(data) // msg_len
    freqs = [0] * 16
    for i in range(0, len(data), msg_len):
        y_bytes = data[i:i+2]
        for j in range(2):
            y_byte = data[i + j] 
            for bit in range(8):
                if (y_byte >> (7 - bit)) & 1:
                    freqs[8*j + bit] += 2
                else:
                    freqs[8*j + bit] += 1
    # Guess each bit by freq[i] / (3*msg_repeat_count) > 0.5? 
    msg_bits = []
    for i in range(16):
        if freqs[i] * 2 > 3 * msg_repeat_count:
            msg_bits.append('1')
        else:
            msg_bits.append('0')
    msg = int(''.join(msg_bits), 2)
    print(f"msg_bits: {msg_bits} -> msg: {msg}")
    p = msg_repeat_count
    return msg, p


def solve(): 
    ys = []
    ps = []
    for i in range(87):
        with open(os.path.join(OUTPUT_DIR, f"{i}.bin"), "rb") as f:
            data = f.read()
            msg_len = get_msg_len(data)
            print(f"File {i}.bin: msg_len = {msg_len}, data_len = {len(data)}")
            msg, p = estimate_and_guess(data, msg_len)
            print(f"({i} + 114) * y % {p} = {msg}")
            y = pow(i + 114, -1, p) * msg % p
            print(f"y = {y}")
            ys.append(y)
            ps.append(p)
    print("ys:", ys)
    print("ps:", ps)

    # fermat's little 
    for i in range(len(ys)):
        # x^(0x101) = y (mod p)
        # x = y^(0x101^-1 mod p-1) (mod p) 
        ys[i] = pow(ys[i], pow(0x101, -1, ps[i] - 1), ps[i])

    # CRT 
    x, _ = crt(ps, ys)
    print(f"x = {x}, flag = {long_to_bytes(x)}")
    
if __name__ == "__main__":
    import os
    import sys

    if not os.path.exists(OUTPUT_DIR):
        print(f"Output directory '{OUTPUT_DIR}' does not exist")
        exit(-1)

    solve()
