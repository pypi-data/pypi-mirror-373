import hashlib
import random
import uuid


def get_code(n=4):
    """
    生成随机验证码，数字和字母的概率各一半
    :param n: 验证码长度
    :return: str
    """
    s = ''
    for i in range(n):
        ret_num = random.randint(0, 9)
        ret_alpha = chr(random.randint(65, 90))
        result = random.choice([ret_num, ret_alpha])
        s += str(result)
    return s


def random_str() -> str:
    """
    唯一随机字符串
    :return: str
    """
    only = hashlib.md5(str(uuid.uuid1()).encode(encoding='UTF-8')).hexdigest()
    return str(only)


def get_code_number(n: int = 6) -> str:
    """
    随机数字
    :param n: 长度
    :return: str
    """
    code = ""
    for i in range(n):
        ch = chr(random.randrange(ord('0'), ord('9') + 1))
        code += ch

    return code


if __name__ == '__main__':
    print(get_code())
    print(random_str())
    print(get_code_number(6))

