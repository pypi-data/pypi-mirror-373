from typing import Union

from Crypto import Random
from Crypto.Cipher import AES
import base64


class AESCipher(object):
    """
    可用于二进制(文件)和字符串加密
    """
    def __init__(self, salt):
        '''
        CBC加密需要一个十六位的key(密钥)和一个十六位iv(偏移量)
        '''
        self.salt = self.check_key(salt)
        # 这里使用随机偏移量
        # self.iv = self.check_key(iv) if iv else self.salt
        # 数据块的大小  16位
        self.BS = AES.block_size
        # CBC模式 相对安全 因为有偏移向量 iv 也是16位字节的
        self.mode = AES.MODE_CBC
        # 填充函数 因为AES加密是一段一段加密的  每段都是BS位字节，不够的话是需要自己填充的
        self.pad = lambda s: s + (self.BS - len(s) % self.BS) * chr(self.BS - len(s) % self.BS).encode('utf-8')
        # 将填充的数据剔除
        self.unpad = lambda s: s[:-ord(s[len(s) - 1:])]

    def encrypt(self, text: Union[bytes, str]) -> bytes:
        text = self.check_data(text)
        text = self.pad(text)
        # 随机获取iv
        iv = Random.new().read(AES.block_size)
        # 初始化自定义
        cipher = AES.new(self.salt, self.mode, iv)
        # 此处是将密文和iv一起 base64 解密的时候就可以根据这个iv来解密
        return base64.b64encode(iv + cipher.encrypt(text))
        # return base64.b64encode(iv + cipher.encrypt(text)).decode("utf-8")

    def decrypt(self, text: Union[bytes, str, int]) -> bytes:
        text = self.check_data(text)
        # 先将密文进行base64解码
        text = base64.b64decode(text)
        # 取出iv值
        iv = text[:self.BS]
        # 初始化自定义
        cipher = AES.new(self.salt, self.mode, iv)
        return self.unpad(cipher.decrypt(text[self.BS:]))
        # return self.unpad(cipher.decrypt(text[self.BS:])).decode("utf-8")

    def check_key(self, key: Union[bytes, str]) -> bytes:
        '''
            检测key的长度是否为16,24或者32bytes的长度
        '''
        if isinstance(key, bytes):
            assert len(key) in [16, 24, 32]
            return key
        elif isinstance(key, str):
            assert len(key.encode("utf-8")) in [16, 24, 32]
            return key.encode("utf-8")
        else:
            raise Exception(f'密钥必须为str或bytes,不能为{type(key)}')

    def check_data(self, data: Union[bytes, str, int]) -> bytes:
        '''
        检测加密的数据类型
        '''
        if isinstance(data, int):
            data = str(data).encode('utf-8')
        elif isinstance(data, str):
            data = data.encode('utf-8')
        elif isinstance(data, bytes):
            pass
        else:
            raise Exception(f'加密的数据必须为str或bytes,不能为{type(data)}')
        return data


# if __name__ == '__main__':
#     # 加密字符串
#     import json
#     # aes_encrypt = AESCipher('ningbozhihuirend')  # 自己设定的密钥
#     aes_encrypt = AESCipher('ningbozhihuirend')  # 自己设定的密钥
#     data = json.dumps({"mobile": "1312345646", "content": "xczczczc"})
#     print(type(data))
#     print(data)
#     e = aes_encrypt.encrypt(data).decode("utf-8")  # 加密内容
#     print(type(e))
#     print(e)
#     d = aes_encrypt.decrypt(e).decode("utf-8")
#     print(type(d))
#     print(json.loads(d))
#     print(len(e))
#     print("加密后%s,解密后%s" % (e, d))
