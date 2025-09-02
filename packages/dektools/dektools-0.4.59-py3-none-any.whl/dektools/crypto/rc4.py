def rc4_str(data: str, key: str):
    s, j, out = list(range(256)), 0, []
    for i in range(256):
        j = (j + s[i] + ord(key[i % len(key)])) % 256
        s[i], s[j] = s[j], s[i]
    i = j = 0
    for char in data:
        i = (i + 1) % 256
        j = (j + s[i]) % 256
        s[i], s[j] = s[j], s[i]
        out.append(chr(ord(char) ^ s[(s[i] + s[j]) % 256]))
    return ''.join(out)


def rc4(data: bytes, key: bytes):
    s, j, out = list(range(256)), 0, []
    for i in range(256):
        j = (j + s[i] + key[i % len(key)]) % 256
        s[i], s[j] = s[j], s[i]
    i = j = 0
    for char in data:
        i = (i + 1) % 256
        j = (j + s[i]) % 256
        s[i], s[j] = s[j], s[i]
        out.append(char ^ s[(s[i] + s[j]) % 256])
    return bytes(out)
