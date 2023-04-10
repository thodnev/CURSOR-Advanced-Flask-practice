import hashlib
import uuid
import random
import os
import datetime as dt
import base64


def iter_chunked(iobuf, chunk_kb=1024):
    size = chunk_kb * 1024
    while True:
        chunk = iobuf.read(size)
        if not chunk:
            return
        yield chunk


def get_hash(iobuf, hashmethod=hashlib.md5, chunk_kb=1024):
    hash = hashmethod()

    saved_pos = iobuf.tell()  # remember position
    iobuf.seek(0)       # rewind buffer

    for chunk in iter_chunked(iobuf, chunk_kb=chunk_kb):
        hash.update(chunk)
    
    iobuf.seek(saved_pos)   # restore file position
    digest = hash.digest()
    return digest


def compare_buffers(iobuf_a, iobuf_b, chunk_kb=1024):
    # first check sizes if differ
    if iobuf_a.seek(0, os.SEEK_END) != iobuf_b.seek(0, os.SEEK_END):
        return False
    
    # now rewind all to the beginning and compare by contents
    iobuf_a.seek(0)
    iobuf_b.seek(0)
    size = chunk_kb * 1024

    while True:
        a, b = iobuf_a.read(size), iobuf_b.read(size)
        if a != b:
            return False
        if not a or not b:
            break
    return True


_uid_time_start = dt.datetime(2023, 1, 1, tzinfo=dt.timezone.utc)
def own_uuid(sequence_number=None, creation_date=None):
    """Our UUID has form:  [gen] or [seq]-[gen]
    [seq] = 6 bytes of item number in a sequence
    Thus, sequence can have a range of up to 10 ** 14 items

    [gen] = [time]-[rand]

    [time] = 6 bytes of tdelta
    where: tdelta is number of microseconds/50 passed
           since 01-01-2023 GMT
    
    [rand] = 6 bytes of random
    
    This way, we're able to represent time
    up to year 2468 with 50 uS resolution.

    Note: all bytes are big endian
    """
    encode = base64.b32hexencode

    if creation_date is None:
        creation_date = dt.datetime.now()
    
    creation_date = creation_date.astimezone(dt.timezone.utc)
    delta = creation_date - _uid_time_start
    delta = int(delta.total_seconds() * (1e6 / 50))
    
    assert delta >= 0, 'UUIDs for items created before 01-01-2023 unsupported'
    
    tdelta = delta.to_bytes(6, 'big', signed=False)
    time = encode(tdelta)[:10]

    rand = random.randbytes(6)
    rand = encode(rand)[:10]

    if sequence_number is not None:
        seq = int(sequence_number)
        seq = seq.to_bytes(6, 'big', signed=False)
        seq = encode(seq)[:10]
        parts = [seq, time, rand]
    else:
        parts = [time, rand]
    

    res = b'-'.join(parts)
    res = res.lower()
    
    return res.decode('ascii')
