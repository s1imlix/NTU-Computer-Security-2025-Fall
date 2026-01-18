from Crypto.Util.number import bytes_to_long, getPrime, isPrime


def gen(d: int):
    p = getPrime(512)
    q = getPrime(512)
    phi = (p - 1) * (q - 1)
    e = pow(d, -1, phi)
    n = p * q
    return n, e


def main():
    with open("flag.txt", "rb") as f:
        flag = f.read().strip()
    d = getPrime(13 * 37)
    pks = [gen(d) for _ in range(42)]

    c = bytes_to_long(flag)
    for n, e in pks:
        c = pow(c, e, n)

    print(f"{pks = }")
    print(f"{c = }")


if __name__ == "__main__":
    main()
