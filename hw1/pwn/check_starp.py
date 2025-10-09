import sys 

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python check_starp.py <path_to_starp_file>")
        sys.exit(1)

    data = []
    with open(sys.argv[1], 'rb') as file:
        # discard first 5 bytes
        data = file.read() 
        data = data[5:]
    
    # function section
    n_func = int.from_bytes(data[:4], "little")
    storage_offset = 4 + n_func * 4
    func = data[4:storage_offset]

    n_storage = int.from_bytes(data[storage_offset:storage_offset + 4], "little") 
    program_offset = storage_offset + 4 + n_storage * 8
    storage = data[storage_offset + 4:program_offset]

    n_program = int.from_bytes(data[program_offset:program_offset + 4], "little")
    program = data[program_offset + 4:]
    print(f"Section sizes: functions={n_func} x 4 bytes, storage={n_storage} x 8 bytes, program={len(program)} bytes")

    print("=== Functions ===")
    print(f"Number of functions: {n_func}")
    func_offsets = []
    for i in range(n_func):
        func_entry = func[i*4:(i+1)*4]
        func_offset = int.from_bytes(func_entry, "little")
        func_offsets.append(func_offset)
    func_offsets.append(len(program))  # end of last function
    for i in range(len(func_offsets) - 1):
        print(f"Function {i}: 0x{func_offsets[i]:x}~0x{func_offsets[i+1]:x}, size={func_offsets[i+1]-func_offsets[i]} bytes")
        for b in program[func_offsets[i]:func_offsets[i+1]]:
            print(f"{b:02x} ", end="")
        print() 
    print('=== Storage ===')
    for i in range(n_storage):
        storage_entry = storage[i*8:(i+1)*8]
        print(f"Storage {i}: {storage_entry.hex()}")

        
