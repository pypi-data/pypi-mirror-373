from typing import Union, Optional, List

from fastgenerateapi.settings.all_settings import settings


def parse_str_to_bool(val: Union[int, str, bool, None]) -> bool:
    """
    解析字符串到布尔值
    """
    if type(val) == bool:
        return val
    elif type(val) == int:
        return val != 0
    elif type(val) == str:
        if val.upper() in ("1", "ON", "TRUE"):
            return True
        elif val.upper() in ("0", "OFF", "FALSE"):
            return False
    return settings.app_settings.DEFAULT_WHETHER_PAGE


def parse_str_to_int(val: Union[int, str, None]) -> int:
    """
    解析字符串到数值
    """
    if type(val) == int:
        return val
    elif type(val) == str:
        try:
            val = int(val)
        except Exception as e:
            val = 0
        return val

    return 0


def parse_str_to_list(val: Optional[str], split_list: Optional[List[str]] = None) -> List[str]:
    """
    某些字段可能由、，,等拼接，字符串分割为列表
    :param val:  我、你，他,她
    :param split_list: 默认 ["、", "，", ","]
    :return: ["我", "你", "他", "她"]
    """
    # 如果输入为空，返回空列表
    if not val:
        return []

    # 设置默认分隔符列表
    if split_list is None:
        split_list = ["、", "，", ","]

    # 初始化结果列表
    result = [val]

    # 遍历分隔符，逐步拆分字符串
    for sep in split_list:
        result = [item for sublist in result for item in sublist.split(sep)]

    # 去除每个元素的前后空格
    result = [item.strip() for item in result]

    # 过滤掉空字符串
    result = [item for item in result if item]

    return result


def number_to_chinese(num):
    """
    数字转换为大写中文，会自动带上整字
    :param num:
    :return:
    """
    if num == 0:
        return "零元整"
    dict1 = {1: '壹', 2: '贰', 3: '叁', 4: '肆', 5: '伍', 6: '陆', 7: '柒', 8: '捌', 9: '玖', 0: '零'}
    dict2 = {2: '拾', 3: '佰', 4: '仟', 5: '万', 6: '拾', 7: '佰', 8: '仟', 1: '元', 9: '角', 10: '分', 11: '整'}
    money = ''
    flag = False
    flag2 = False
    count = 0
    count2 = 8
    strnum = str(num)
    aa = strnum.split('.')
    bb = list(str(aa[:1])[2:-2])
    cc = list(str(aa[1]).rstrip("0")[:2]) if len(aa) > 1 else []

    for i in reversed(bb):
        count = count + 1
        if int(i) == 0:
            if flag:
                if count != 5:
                    continue
                else:
                    money = dict2[count] + money
            else:
                if not flag2:
                    money = dict2[count] + money
                else:
                    if count != 5:
                        money = '零' + money
                    else:
                        money = dict2[count] + '零' + money
            flag = True
        else:
            flag = False
            flag2 = True
            money = dict1[int(i)] + dict2[count] + money
    for i in cc:
        count2 = count2 + 1
        money = money + dict1[int(i)] + dict2[count2]

    return money + '整'


if __name__ == '__main__':
    # test parse_str_to_list
    print(parse_str_to_list("我、你，他,她"))
    print(parse_str_to_list("我|你&他 她", split_list=["|", "&", " "]))
