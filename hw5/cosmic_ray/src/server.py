import math
import os
import secrets
import signal

from Crypto.Util.number import getPrime


def keygen(bits: int):
    e = 17
    while True:
        p = getPrime(bits // 2)
        q = getPrime(bits // 2)
        n = p * q
        lam = (p - 1) * (q - 1) // math.gcd(p - 1, q - 1)
        if math.gcd(e, lam) == 1:
            d = pow(e, -1, lam)
            return n, e, d


def cosmic_ray(x: int):
    return x + secrets.randbits(20)


def main():
    n, e, d = keygen(2048)
    print(f"{n = }")
    print(f"{e = }")
    c1 = pow(cosmic_ray(d), e, n)
    c2 = pow(cosmic_ray(d), e, n)
    print(f"{c1 = }")
    print(f"{c2 = }")

    signal.alarm(69)

    x = int(input("x = "))
    if pow(x, 0x1337, n) == 42:
        print(os.environ.get("FLAG", "FLAG{test_flag}"))
    else:
        print(":(")


if __name__ == "__main__":
    main()
