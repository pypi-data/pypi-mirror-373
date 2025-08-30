import mimetypes
import shutil
import traceback

import send2trash

from .system import *


def fileSizeAddUnit(value: int, is_binary: bool = True):
    """
    文件比特大小加单位（1024进制）。
    :param value: 值
    :return: 字符串
    """
    if is_binary:
        units = ["B", "KiB", "MiB", "GiB", "TiB", "PiB", "EiB", "ZiB", "YiB", "BiB"]
        size = 1024.0
    else:
        units = ["B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB", "BB"]
        size = 1000.0
    for i in range(len(units)):
        if (value / size) < 1:
            return f"{value:.2f}{units[i]}"
        value = value / size
    return f"{value:.2f}BB"


sizeAddUnit = fileSizeAddUnit


def formatPathString(path: str):
    """
    格式化路径
    :param path: 路径
    :return: 格式化结果
    """
    return os.path.normpath(path)


formatPath = formatPathString


def joinPath(*paths):
    """
    拼接路径。
    :param paths: 多个字符串参数
    :return:
    """
    return formatPathString(os.path.join("", *paths))


pathJoin = joinPath


def isSamePath(path1: str, path2: str):
    """
    判断路径是否相同
    :param path1: 路径1
    :param path2: 路径2
    :return: 是否相同
    """
    return os.path.samefile(path1, path2) if existPath(path1) and existPath(path2) else False


samePath = isSamePath


def existPath(path: str):
    """
    判断路径是否存在。
    :param path: 路径
    :return: 是否存在
    """
    return os.path.exists(path)


exist = exists = pathExists = pathExist = existPaths = existPath


def isFile(path: str):
    """
    判断路径是否为文件
    :param path: 路径
    :return: 是否为文件
    """
    return os.path.isfile(path) if existPath(path) else False


def isDir(path: str):
    """
    判断路径是否为目录
    :param path: 路径
    :return: 是否为目录
    """
    return os.path.isdir(path) if existPath(path) else False


def renamePath(old: str, new: str):
    """
    重命名路径
    :param old: 旧路径
    :param new: 新路径
    :return:
    """
    os.rename(old, new)
    return existPath(new)


rename = renamePath


def deleteFile(path: str, trash: bool = False, force: bool = False):
    """
    删除文件
    :param path: 文件路径
    :param trash: 是否删除到回收站
    :param force: 是否强制删除，优先级低于回收站
    :return: 是否删除成功
    """
    if not existPath(path):
        logging.warning(f"文件{path}不存在，无法删除！")
        return
    try:
        if trash:
            send2trash.send2trash(path)
        elif force:
            easyCmd(f'del /F /Q /S "{path}"', True)
        else:
            os.remove(path)
    except Exception as ex:
        logging.error(f"删除文件{path}失败，错误信息为{ex}，回收站删除模式为{trash}，强制删除模式为{force}。")
    return not existPath(path)


def deleteDir(path: str, trash: bool = False, force: bool = False):
    """
    删除目录
    :param path: 目录路径
    :param trash: 是否删除到回收站
    :param force: 是否强制删除，优先级低于回收站
    :return: 是否删除成功
    """
    if not existPath(path):
        logging.warning(f"文件夹{path}不存在，无法删除！")
        return False
    try:
        if trash:
            send2trash.send2trash(path)
        elif force:
            easyCmd(f'rmdir /S /Q "{path}"', True)
        else:
            shutil.rmtree(path)
    except Exception as ex:
        logging.error(f"删除文件夹{path}失败，错误信息为{ex}，回收站删除模式为{trash}，强制删除模式为{force}。")
    return not existPath(path)


def deletePath(path: str, trash: bool = False, force: bool = False):
    """
    删除文件或目录
    :param path: 文件或目录路径
    :param trash: 是否删除到回收站
    :param force: 是否强制删除，优先级低于回收站
    :return:
    """
    if isFile(path):
        deleteFile(path, trash, force)
    elif isDir(path):
        deleteDir(path, trash, force)
    return not existPath(path)


delete = deletePath


def getFileName(path: str, has_suffix: bool = True):
    """
    获取文件名
    :param path: 文件路径
    :param has_suffix: 有无后缀名
    :return: 文件名
    """
    if has_suffix:
        return os.path.basename(path)
    else:
        return os.path.splitext(os.path.basename(path))[0]


def getFileSuffix(path: str, from_name: bool = True, default="", has_dot: bool = True):
    """
    获取文件后缀名
    :param path: 文件路径
    :param from_name: 是否从文件名称获取后缀名
    :param has_dot: 是否包含后缀名开头的点
    :return: 文件后缀名
    """
    if from_name:
        suffix = os.path.splitext(os.path.basename(path))[1]
    else:
        try:
            import puremagic
            with open(path, "rb") as f:
                ext = puremagic.from_string(f.read(1024))
                suffix = ext if ext else default
        except Exception:
            suffix = default
            logging.error(f"识别本地文件{path}类型失败，使用默认类型{default}，报错信息：{traceback.format_exc()}！")
    if not has_dot:
        suffix = suffix.lstrip(".")
    return suffix


getSuffix = getFileSuffix


def getFileDir(path: str):
    """
    获取文件所在目录
    :param path: 文件路径
    :return: 文件所在目录
    """
    return os.path.dirname(path)


getDirName = getFileDir


def createDir(path: str):
    """
    创建目录
    :param path: 目录路径
    """
    if not existPath(path):
        os.makedirs(path)
    return existPath(path)


def createFile(path: str):
    """
    创建空文件
    :param path: 文件路径
    """
    if not existPath(path):
        open(path, "w").close()
    return existPath(path)


def fileSize(path: str):
    """
    获取文件大小
    :param path: 文件路径
    :return: 文件大小
    """
    if isFile(path):
        return os.path.getsize(path)
    else:
        logging.warning(f"未知路径{path}，无法计算大小。")
        return False


def dirSize(path: str):
    """
    获取路径大小
    :param path: 路径
    :return: 路径大小
    """
    if isDir(path):
        return sum([fileSize(joinPath(path, file)) for file in walkFile(path)])
    else:
        logging.warning(f"未知路径{path}，无法计算大小。")
        return False


def pathSize(path: str):
    """
    获取路径大小
    :param path: 路径
    :return: 路径大小
    """
    if isFile(path):
        return fileSize(path)
    elif isDir(path):
        return dirSize(path)
    else:
        logging.warning(f"未知路径{path}，无法计算大小。")
        return False


size = pathSize


def fileHash(path: str, mode: str = "md5"):
    """
    获取文件哈希值
    :param path: 文件路径
    :param mode: 哈希算法，支持md5、sha1、sha256
    :return: 哈希值
    """
    if not isFile(path):
        logging.warning(f"文件{path}不存在，无法获取哈希值。")
        return None
    if mode == "md5":
        from hashlib import md5
        return md5(open(path, "rb").read()).hexdigest()
    elif mode == "sha1":
        from hashlib import sha1
        return sha1(open(path, "rb").read()).hexdigest()
    elif mode == "sha256":
        from hashlib import sha256
        return sha256(open(path, "rb").read()).hexdigest()


def checkFileHash(path: str, hash: str, mode: str = "md5"):
    """
    检查文件哈希值是否为指定值
    :param path: 文件路径
    :param hash: 需要判断的已知哈希值
    :param mode: 哈希算法，支持md5、sha1、sha256
    :return: 是否相同
    """
    return bool(fileHash(path, mode).lower() == hash.lower())


def walkFile(path: str, only_first: bool = False):
    """
    遍历目录
    :param path: 目录路径
    :param only_first: 模式：是否只包含第一层的文件
    :return: 文件名列表
    """
    l1 = []
    if existPath(path):
        if only_first:
            for i in os.listdir(path):
                if isFile(joinPath(path, i)):
                    l1.append(joinPath(path, i))
        else:
            if isDir(path):
                paths = os.walk(path)
                for path, dir_lst, file_lst in paths:
                    for file_name in file_lst:
                        l1.append(joinPath(path, file_name))

    return sorted(l1)


def walkDir(path: str, only_first: bool = False):
    """
    遍历子文件夹
    :param path: 目录路径
    :param only_first: 模式：是否只包含第一层的文件夹
    :return: 目录名列表
    """
    l1 = []
    if existPath(path):
        if only_first:
            for i in os.listdir(path):
                if isDir(joinPath(path, i)):
                    l1.append(joinPath(path, i))
        else:
            if isDir(path):
                paths = os.walk(path)
                for path, dir_lst, file_lst in paths:
                    for dir_name in dir_lst:
                        l1.append(joinPath(path, dir_name))
    return sorted(l1)


def walkPath(path: str, only_first: bool = False):
    """
    遍历子文件和子文件夹
    :param path: 目录路径
    :param only_first: 模式：是否只包含第一层的文件（夹）
    :return: 目录名列表
    """
    l1 = []
    if existPath(path):
        if only_first:
            for i in os.listdir(path):
                l1.append(joinPath(path, i))
        else:
            if isDir(path):
                paths = os.walk(path)
                for path, dir_lst, file_lst in paths:
                    for name in dir_lst + file_lst:
                        l1.append(joinPath(path, name))
    return sorted(l1)


walk = walkPath


def setOnlyRead(path: str, enable: bool):
    """
    只读权限
    :param path: 文件路径
    :param enable: 启用/禁用
    """
    from stat import S_IREAD, S_IWRITE
    if isFile(path):
        if enable:
            os.chmod(path, S_IREAD)
        else:
            os.chmod(path, S_IWRITE)


def getRepeatFileName(path: str):
    """
    添加重复后缀（用于复制文件的时候解决名称重复问题）
    :param path: 新文件本身路径
    :return: 新文件本身路径
    """
    if isFile(path):
        i = 1
        while existPath(joinPath(getFileDir(path), getFileName(path, False) + " (" + str(i) + ")" + getFileSuffix(path))):
            i += 1
        path = joinPath(getFileDir(path), getFileName(path, False) + " (" + str(i) + ")" + getFileSuffix(path))
    elif isDir(path):
        i = 1
        while existPath(path + " (" + str(i) + ")"):
            i += 1
        path = path + " (" + str(i) + ")"
    return path


getRepeatName = repeatName = repeatFileName = getRepeatFileName


def copyPath(old: str, new: str, replace: bool = False):
    """
    复制文件
    :param old: 原文件路径
    :param new: 目标路径
    :param replace: 文件重复时是否替换，关闭时将在复制后位置添加序号
    :return: 是否成功
    """
    if not existPath(old):
        logging.error(f"文件{old}不存在，无法复制！")
        return False
    if existPath(new) and replace or fileSize(new) == 0:
        logging.warning(f"文件{new}已存在，将尝试以{old}替换！")
        deletePath(new)
    if not replace:
        new = getRepeatFileName(new)
    if isFile(old):
        try:
            createDir(getFileDir(new))
            shutil.copy2(old, new)
        except Exception as ex:
            logging.error(f"复制文件失败，错误信息：{ex}。")
            return False
    elif isDir(old):
        try:
            shutil.copytree(old, new)
        except Exception as ex:
            logging.error(f"复制文件夹失败，错误信息：{ex}。")
            return False
    return new if existPath(new) else False


copy = copyPath


def movePath(old: str, new: str, replace: bool = False):
    """
    移动文件（夹）
    :param old: 旧文件（夹）自身路径
    :param new: 新文件（夹）所在或本身路径
    :param replace: 文件重复时是否替换，关闭时将在复制后位置添加序号
    """
    if not existPath(old):
        logging.error(f"文件{old}不存在，无法移动！")
        return False
    new = copyPath(old, new, replace)
    if new:
        deletePath(old)
    return new if existPath(new) and not existPath(old) else False


move = movePath


def clearDir(path: str):
    """
    删除文件夹内的所有文件（无法删除则跳过）
    :param path: 路径
    """
    if isDir(path):
        for i in walkPath(path, True):
            deletePath(i)


def showFile(path: str):
    """
    在文件资源管理器中打开目录
    :param path: 路径
    """
    if isFile(path):
        easyCmd(f'explorer /select,"{path.replace("/", "\\")}"')
    elif isDir(path):
        os.startfile(path)


def startFile(path: str, bind: bool = False):
    """
    运行文件（不与程序进程绑定）
    :param path: 路径
    :param bind: 是否与当前进程绑定
    """
    if isFile(path):
        if bind:
            easyCmd(f'"{path}"')
        else:
            easyCmd(f'start "" /B "{path}"')


def extractZip(path: str, goal: str, delete: bool = False):
    """
    解压zip文件
    :param path: zip文件路径
    :param goal: 解压到的目录路径
    :param delete: 解压后删除
    """
    import zipfile
    if existPath(path):
        try:
            file = zipfile.ZipFile(path)
            file.extractall(goal)
            file.close()
            if delete:
                deleteFile(path)
            logging.debug(f"{path}解压成功！")
        except Exception as ex:
            logging.warning(f"{path}解压失败{ex}！")
