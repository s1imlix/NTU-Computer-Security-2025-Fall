from pwn import *
from random import randbytes

def opcode_payload(opcode: int) -> bytes:
    return p8(opcode).ljust(8, b'\x00')

p = remote('127.0.0.1', 33827)

print(p.recv(8))
print(p.recv(44))

print('=== key exchange ===')
payload = b'\x00' * 4 + b',' + b'\x00' * 3
p.send(payload)
prob_key = randbytes(44)
p.send(prob_key)
print(f'sent key? {prob_key.hex()}')

p.send(opcode_payload(0x5))
print(f'sent opcode 0x5')
size = u32(p.recv(8)[4:])
print(f'size: {size}')
print(p.recv(size).hex())
