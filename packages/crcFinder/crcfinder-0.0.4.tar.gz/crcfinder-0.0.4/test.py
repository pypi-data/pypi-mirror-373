#from crcFinder import CrcFinder
#import zlib
#
#data = []
#data.append((b"123456789", zlib.crc32(b'123456789')))
#data.append((b"123456789xxxx", zlib.crc32(b'123456789xxxx')))
#f = CrcFinder()
#r = f.findCrc(data)
#print([str(i) for i in r])
#
from crcFinder import CrcFinder
data = []
data.append((b"123456789\x09", b'\x11\x60\x7a\x37'))
data.append((b"1234567890\x0a", b'\xb3\x95\xcb\x46'))
f = CrcFinder()
r = f.findCrc(data)
print(r[0])