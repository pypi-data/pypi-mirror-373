from Crypto.Cipher import AES
from Crypto.Util.Padding import pad as pad_base, unpad as unpad_base


def pad(data_to_pad, block_size, style):
    if style == 'pkcs5':
        pad_len = block_size - len(data_to_pad) % block_size
        return data_to_pad + (bytes([pad_len]) * pad_len)
    else:
        return pad_base(data_to_pad, block_size, style)


def unpad(padded_data, block_size, style):
    if style == 'pkcs5':
        return padded_data[:-ord(padded_data[-1:])]
    else:
        return unpad_base(padded_data, block_size, style)


class CryptoBase:
    KEY = None
    IV = None

    encoding_key = 'utf-8'
    encoding_iv = 'utf-8'
    style = 'pkcs7'
    mode = AES.MODE_CBC

    @property
    def cipher(self):
        return AES.new(self.KEY.encode(self.encoding_key), mode=self.mode, iv=self.IV.encode(self.encoding_iv))

    def _encrypt(self, bs):
        bs = pad(bs, AES.block_size, self.style)
        bs = self.cipher.encrypt(bs)
        return bs

    def _decrypt(self, bs):
        bs = self.cipher.decrypt(bs)
        bs = unpad(bs, AES.block_size, self.style)
        return bs
