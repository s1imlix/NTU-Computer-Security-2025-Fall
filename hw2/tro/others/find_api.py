def rol32(v, bits):
    v &= 0xFFFFFFFF
    return ((v << bits) | (v >> (32 - bits))) & 0xFFFFFFFF

def hash_asm_style(name: str) -> int:
    """
    Emulate the exact assembly:
      mov ecx,eax
      rol ecx,11
      lea eax,[rax+rcx+0x4A3]
      movsx ecx, byte ptr [rdx]
      add eax, ecx
      add rdx,1
      cmp byte ptr [rdx],0
      jnz loop
    """
    b = name.encode('ascii', 'ignore') + b'\x00'  # ensure a terminating NUL like in C
    eax = 0
    i = 0
    while True:
        ecx = rol32(eax, 11)
        eax = (eax + ecx + 0x4A3) & 0xFFFFFFFF
        byte = b[i]
        # movsx: sign-extend 8-bit to 32-bit
        if byte & 0x80:
            sb = byte - 0x100
        else:
            sb = byte
        eax = (eax + (sb & 0xFFFFFFFF)) & 0xFFFFFFFF
        i += 1
        # cmp byte ptr [rdx], 0  -> check next byte after increment
        if b[i] == 0:
            break
    return eax

# example usage
target = 0xCD841E17
names = None
with open("./msvcrt.dll.txt", "r") as f:
    names = [line.strip() for line in f.readlines()]
    # print(names)
for name in names:
    h = hash_asm_style(name)
    if h == target:
        print(f"Found match: {name} -> 0x{h:08X} ({h}) in msvcrt.dll")

target_list = [0x5F00766C, 0x6D555364, 0x42B4FA0, 0xC473C85A]
names = None
with open("./kernel32.dll.txt", "r") as f:
    names = [line.strip() for line in f.readlines()]
    # print(names)

for target in target_list:
    for name in names:
        h = hash_asm_style(name)
        if h == target:
            print(f"Found match: {name} -> 0x{h:08X} ({h}) in kernel32.dll")

