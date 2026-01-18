from pwn import *
import binascii
# --- CONFIGURE ---
HOST = "10.113.0.1"
PORT = 35001

# Block size is AES (16 bytes)
BLOCK_SIZE = 16

# Custom oracle client
def oracle(p, data_hex):
    # print(f'asking oracle with: {data_hex}')
    p.sendline(data_hex.encode())
    resp = p.recvline().decode()
    if 'Well received' in resp:
        # print(f'{resp}')
        return "Well received" in resp

def split_blocks(data, block_size=BLOCK_SIZE):
    return [data[i:i+block_size] for i in range(0, len(data), block_size)]

def recover_block(p, prev, curr, init_chk):
    recovered = bytearray(BLOCK_SIZE)
    intermediate = bytearray(BLOCK_SIZE)
    pos = BLOCK_SIZE - 2
    chk = 0
    for guess in range(256):
        pad = (init_chk & 0x0f)
        modified_prev = bytearray(prev)
        modified_prev[BLOCK_SIZE - 1] = guess ^ pad
        modified_ct = bytes(modified_prev) + curr
        modified_ct_hex = binascii.hexlify(modified_ct).decode()
        if oracle(p, modified_ct_hex):
            intermediate[BLOCK_SIZE - 1] = guess 
            recovered[BLOCK_SIZE - 1] = intermediate[BLOCK_SIZE - 1] ^ prev[BLOCK_SIZE - 1]
            print(chr(recovered[BLOCK_SIZE - 1]))
    while pos >= 0:
        """
            scheme
            (pad length - 1) | chk 
        """
        pad = (BLOCK_SIZE - pos - 1) << 4 | (chk & 0x0f)
        """
        Note that by sending Ci-1 = g xor (length | 0x0)
        with padding check passed, we very likely got 0x0(chk) where chk = checksum(Ci-1Ci)
        no need to brute-force the lower 4-bits as we'll get another g' 
        s.t. Ci-1 = g' xor (length | chk) == g xor (length | 0x0)
        -> there're total 16 pairs of (g, chk) that work while only one g is the intermediate byte we want
        """
        found = False
        for guess in range(256): 
            # Construct modified previous block
            modified_prev = bytearray(prev)
            modified_prev[pos] = guess ^ pad
            for k in range(pos + 1, BLOCK_SIZE):
                modified_prev[k] = intermediate[k] ^ pad
                
            modified_ct = bytes(modified_prev) + curr
            modified_ct_hex = binascii.hexlify(modified_ct).decode()
            if oracle(p, modified_ct_hex):
                intermediate[pos] = guess 
                recovered[pos] = intermediate[pos] ^ prev[pos]
                print(chr(recovered[pos]))
                found = True
                chk = 0
                pos -= 1
                break # a valid (g, chk) for this byte found, move to next byte
        if not found:
            chk += 1
    return bytes(recovered)

def main():
    # Connect to service
    p = remote(HOST, PORT)
    # Receive initial ciphertext
    ct_hex = p.recvline().decode().strip()
    ct = bytes.fromhex(ct_hex)
    # Split into blocks
    blocks = split_blocks(ct, BLOCK_SIZE)
    num_blocks = len(blocks)
    recovered_plaintext = []
    # Perform oracle attack for each block
    precomputed_chks = [0x06, 0x0f] 
    for i in range(1, num_blocks):
        chk = precomputed_chks[i - 1]
        print(f'Block {i}, trying chk={chk:02x}')
        recovered = recover_block(p, blocks[i-1], blocks[i], chk)
        if len(recovered) < BLOCK_SIZE:
            break
        recovered_plaintext.append(recovered)
        print(f'Block {i} recovered: {recovered}')
    recovered_plaintext = b''.join(recovered_plaintext)
    print(f'Recovered plaintext: {recovered_plaintext}')

if __name__ == "__main__":
    main()

