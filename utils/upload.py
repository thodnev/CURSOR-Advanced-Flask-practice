import hashlib
import uuid
import random

def get_file_hash(filename, hashmethod=hashlib.md5, chunk_kb=1024):
    size = chunk_kb * 1024
    hash = hashmethod()
    with open(filename, 'rb') as file:
        chunk = file.read(size)
        while chunk:
            hash.update(chunk)
            chunk = file.read(size)
            if not chunk:
                break
    
    digest = hash.hexdigest()
    return digest


#UUID_IMG_NODE = 0x1d9e75ea6a97      # instead of machine ID
def get_uuid():
    node = random.getrandbits(48)
    u = uuid.uuid1(node=node)
    return u.bytes.hex()
