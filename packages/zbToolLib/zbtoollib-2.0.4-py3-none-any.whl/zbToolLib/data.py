from zbToolLib import SYSTEM_TYPE


def clearEscapeCharaters(text: str):
    """
    清理字符串中的转义字符
    :param text: 字符串
    :return: 清理后的字符串
    """
    from re import sub
    return sub(r"[\n\v\r\t]", "", text)


def clearIllegalPathName(text: str):
    """
    清理违规路径
    :param text: 字符串
    :return: 清理后的字符串
    """
    from re import sub
    if SYSTEM_TYPE == "Windows":
        return sub(r'[*?"<>|]', "", text)
    elif SYSTEM_TYPE == "MacOS":
        return sub(r'[:]', "", text)
    else:
        return text


def compareVersionCode(version1: str, version2: str):
    """
    比较版本号大小，仅支持如1.0.0的不含字符的版本号
    :param version1: 版本号1
    :param version2: 版本号2
    :return: 返回大的版本号
    """
    list1: list = version1.split(".")
    list2: list = version2.split(".")
    for i in range(len(list1)) if len(list1) < len(list2) else range(len(list2)):
        if int(list1[i]) == int(list2[i]):
            pass
        elif int(list1[i]) < int(list2[i]):
            return version2
        else:
            return version1
    if len(list1) >= len(list2):
        return version1
    else:
        return version2


def sortVersionCode(version: list, key=lambda x: x, reverse: bool = False):
    """
    版本号列表排序
    :param version: 版本号列表
    :param reverse: 是否降序
    :param repeat: 是否允许重复版本
    :return: 排序
    """
    version.sort(key=lambda x: tuple(int(v) for v in key(x).split(".")), reverse=reverse)
    return version


def numberAddUnit(value: int):
    """
    数字加单位
    :param value: 值
    :return: 字符串
    """
    units = ["", "万", "亿", "兆"]
    size = 10000.0
    for i in range(len(units)):
        if (value / size) < 1:
            return f"{value:.{i}f}{units[i]}"
        value = value / size
    return f"{value:.3f}兆"


def getInfo(data, key, default="无"):
    """
    从data字典获取key项的值，若不存在或为空则返回default值
    :param data: 字典
    :param key: 键名
    :param default: 默认值
    :return:
    """
    if key in data.keys() and data[key] != "" and data[key] is not None:
        return data[key]
    else:
        return default
