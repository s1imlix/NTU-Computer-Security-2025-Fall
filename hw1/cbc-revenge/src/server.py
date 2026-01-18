from Crypto.Cipher import AES
import os


def checksum(data):
    chk = 0
    for x in data:
        chk ^= x
        chk = (13 * chk + 37) & 0xF
    return chk


def pad(data, block_size):
    chk = checksum(data)
    rem = block_size - len(data) % block_size
    byte = ((rem - 1) << 4) | chk
    data += bytes([byte] * rem)
    return data


def unpad(data, block_size):
    byte = data[-1]
    rem = (byte >> 4) + 1
    chk = byte & 0xF
    for b in data[-rem:]:
        if b != byte:
            raise ValueError("Invalid padding")
    data = data[:-rem]
    if checksum(data) == chk:
        return data
    raise ValueError("Invalid padding")


def main():
    with open("flag.txt", "rb") as f:
        flag = f.read().strip()
    key = os.urandom(16)
    cipher = AES.new(key, AES.MODE_CBC)
    ct = cipher.encrypt(pad(flag, AES.block_size))
    iv = cipher.iv
    print((iv + ct).hex())

    while True:
        try:
            inp = bytes.fromhex(input().strip())
            iv, ct = inp[:16], inp[16:]
            cipher = AES.new(key, AES.MODE_CBC, iv)
            unpad(cipher.decrypt(ct), AES.block_size)
            print("Well received :)")
        except ValueError:
            print("Something went wrong :(")


if __name__ == "__main__":
    main()
