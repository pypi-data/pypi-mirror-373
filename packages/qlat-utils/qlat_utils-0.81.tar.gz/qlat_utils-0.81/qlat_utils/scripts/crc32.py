import sys
import zlib

def crc32(fileName):
    with open(fileName, 'rb') as fh:
        hash = 0
        while True:
            s = fh.read(65536)
            if not s:
                break
            hash = zlib.crc32(s, hash)
        return "%08x" % (hash & 0xFFFFFFFF)

for v in sys.argv[1:]:
    print(f"{crc32(v)} '{v}'")

exit()
