from pwn import *
from sage.all import *
from tqdm import tqdm
from multiprocessing import Pool, cpu_count
import gmpy2
import time
import requests
import signal

def solve():
    io = remote('10.113.0.1', 35003)

    signal.alarm(69)

    io.recvuntil(b'n = ')
    n = int(io.recvline().strip())
    io.recvuntil(b'e = ')
    e = int(io.recvline().strip())
    io.recvuntil(b'c1 = ')
    c1 = int(io.recvline().strip())
    io.recvuntil(b'c2 = ')
    c2 = int(io.recvline().strip())

    print(f'{n},{e},{c1},{c2}')

    # Run p, q on workstation
    result = input('p, q > ')
    p, q = map(int, result.split(','))

    phi_n = (p - 1) * (q - 1)

    x = pow(42, pow(0x1337, -1, phi_n), n)

    info(f'Sending x: {x}')
    io.sendline(str(x).encode())
    info(io.recvline().decode().strip())

if __name__ == "__main__":
    solve()