import random

from passlib.hash import pbkdf2_sha256, md5_crypt


def make_random_salt(length=64):
    """
        生成随机salt字符串，可指定长度
    :param length: int
    :return: salt: str
    """
    seed = "1234567890abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ!#$&*="
    sa = []
    for i in range(length):
        sa.append(random.choice(seed))
    salt = ''.join(sa)
    return salt


def create_password_hash(password: str, salt: str) -> str:
    """
    根据传入的password与salt参数生成hash值
    :param password:
    :param salt:
    :return:
    """
    custom_pbkdf2 = pbkdf2_sha256.using(salt=salt.encode('utf-8'), rounds=1000)
    return custom_pbkdf2.hash(password)


def validate_password(password: str, salt: str, password_hash: str) -> bool:
    """
    password 校验
    :param password:
    :param salt:
    :param password_hash:
    :return:
    """
    validating_password_hash = create_password_hash(password, salt)
    return validating_password_hash == password_hash


# if __name__ == '__main__':
#     # salt = make_random_salt(length=60)
#     salt = "lpiZRQwWoj&*wh29Jovk$uA3YGP$TSQYpM4ooy1z3zGuNT=vmLpb&Ves"
#     hash_str = create_password_hash('123456132312312312312321', salt)
#     print(hash_str)
#     print(len(hash_str))
#     print(validate_password(password='123456132312312312312321', salt=salt, password_hash=hash_str))
