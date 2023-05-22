import struct

str = ''
empty_str = ''
str = str.encode()
empty_str = empty_str.encode()

packed = struct.pack('!c4H256s', '+'.encode(), 2133, 234, 11, 3245, str)
print(struct.calcsize('!c4H'))
print(packed)
func, arg0, arg1, arg2, arg3, message = struct.unpack('!c4H256s',packed)
print(func, arg0, arg1, arg2, arg3, message.decode())

