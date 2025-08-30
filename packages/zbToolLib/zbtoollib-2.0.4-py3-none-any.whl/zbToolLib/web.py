import re
import traceback
from concurrent.futures import ThreadPoolExecutor, wait

import requests

from .file import *
from .info import *


def getWebFileType(url: str, default="", has_dot: bool = True):
    """
    获取指定url文件的后缀名
    :param url: 链接
    :param default: 默认后缀名（无法判断时返回）
    :param has_dot: 是否包含后缀名开头的点
    :return: 文件后缀名
    """
    try:
        import puremagic
        with requests.get(url, stream=True, verify=False) as response:
            response.raise_for_status()
            buffer = next(response.iter_content(1024)).strip()
        ext = puremagic.from_string(buffer)
        suffix = ext if ext else default
        return suffix
    except Exception:
        logging.error(f"识别在线文件{url}类型失败，使用默认类型{default}，报错信息：{traceback.format_exc()}！")
        suffix = default
    if not has_dot:
        suffix = suffix.lstrip(".")
    return suffix


def isUrl(url: str):
    """
    判断是否是网址
    :param url: 网址字符串
    :return: 布尔值
    """
    return bool(re.compile(r"(https?|ftp|file)://[-A-Za-z0-9+&@#/%?=~_|!:,.;]+[-A-Za-z0-9+&@#/%=~_|]").match(url))


def joinUrl(*urls):
    """
    拼接网址
    :param urls: 网址
    :return: 拼接结果
    """
    from urllib.parse import urljoin
    data = ""
    for i in urls:
        data = urljoin(data, i)
    return data


def splitUrl(url: str):
    """
    分割网址
    :param url: 网址
    :return: urlparse对象，使用scheme、netloc、path、params、query、fragment获取片段
    """
    from urllib.parse import urlparse
    return urlparse(url)


def getUrlScheme(url: str):
    """
    获取网址的协议
    :param url: 网址
    :return: 协议
    """
    from urllib.parse import urlparse
    return urlparse(url).scheme


def getUrlNetloc(url: str):
    """
    获取网址的主机名
    :param url: 网址
    :return: 主机名
    """
    from urllib.parse import urlparse
    return urlparse(url).netloc


getUrlHost = getUrlHostname = getUrlDomain = getUrlNetloc


def getUrlPath(url: str):
    """
    获取网址的路径
    :param url: 网址
    :return: 路径
    """
    from urllib.parse import urlparse
    return urlparse(url).path


def getUrlParams(url: str):
    """
    获取网址的参数
    :param url: 网址
    :return: 参数格式如{'keyword': ['abc'], 'id': ['12']}
    """
    from urllib.parse import urlparse, parse_qs
    return parse_qs(urlparse(url).params)


def getUrl(url: str, times: int = 5, **kwargs):
    """
    可重试的get请求
    :param url: 链接
    :param header: 请求头
    :param timeout: 超时
    :param times: 重试次数
    :return:
    """
    logging.info(f"正在Get请求{url}的信息！")
    for i in range(times):
        try:
            response = requests.get(url, **kwargs, stream=True, verify=False)
            logging.info(f"Get请求{url}成功！")
            return response
        except Exception as ex:
            logging.warning(f"第{i + 1}次Get请求{url}失败，错误信息为{ex}，正在重试中！")
            continue
    logging.error(f"Get请求{url}失败！")


def postUrl(url: str, times: int = 5, **kwargs):
    """
    可重试的post请求
    :param url: 链接
    :param times: 重试次数
    :return:
    """
    logging.info(f"正在Post请求{url}的信息！")
    for i in range(times):
        try:
            response = requests.post(url, **kwargs, verify=False)
            logging.info(f"Post请求{url}成功！")
            return response
        except Exception as ex:
            logging.warning(f"第{i + 1}次Post请求{url}失败，错误信息为{ex}，正在重试中！")
            continue
    logging.error(f"Post请求{url}失败！")


def getFileNameFromUrl(url: str):
    """
    从链接获取文件名
    :param url: 链接
    :return:
    """
    return os.path.basename(splitUrl(url).path)


def singleDownload(url: str, path: str, exist: bool = True, force: bool = False, header: dict = REQUEST_HEADER):
    """
    下载文件
    :param url: 下载链接
    :param path: 下载后完整目录/文件名
    :param exist: 是否在已有文件的情况下下载（False时force无效）
    :param force: 是否强制下载（替换已有文件）
    :param header: 请求头
    :return:
    """
    try:
        if isDir(path):
            path = joinPath(path, getFileNameFromUrl(url))
        if isFile(path) and not exist:
            logging.warning(f"由于文件{path}已存在，自动跳过单线程下载！")
            return False
        createDir(getFileDir(path))
        if exist and not force:
            path = getRepeatFileName(path)
        logging.info(f"正在单线程下载文件{url}到{path}！")
        response = requests.get(url, headers=header, stream=True, verify=False)
        with open(path, "wb") as f:
            for chunk in response.iter_content(chunk_size=1024):
                if chunk:
                    f.write(chunk)
        logging.info(f"已将文件{url}单线程下载到{path}！")
        return path
    except Exception as ex:
        deletePath(path)
        logging.error(f"单线程下载文件{url}到{path}失败，报错信息：{ex}！")
        return False


class DownloadManager:
    downloadThreadPool = ThreadPoolExecutor(max_workers=32)
    futures = []

    def setMaxThread(self, num: int):
        if num <= 0:
            logging.error(f"设置多线程下载线程数{num}无效！")
            return False
        self.downloadThreadPool._max_workers = num
        return True

    def download(self, url: str, path: str, exist: bool = True, force: bool = False, header: dict = REQUEST_HEADER):
        """
        下载文件
        :param url: 下载链接
        :param path: 下载后完整目录/文件名
        :param exist: 是否在已有文件的情况下下载（False时force无效）
        :param force: 是否强制下载（替换已有文件）
        :param header: 请求头
        :return: 下载对象
        """
        d = DownloadSession()
        d.download(url, path, self, exist, force, header)
        self.futures.append(d.session)
        return d

    def wait(self):
        """
        等待所有下载完成
        :return:
        """
        wait(self.futures)


class DownloadSession:
    _cancel = False
    _progress = 0
    _result = None
    session = None

    def _download(self, url: str, path: str, exist: bool = True, force: bool = False, header: dict = REQUEST_HEADER):
        try:
            if isDir(path):
                path = joinPath(path, getFileNameFromUrl(url))
            if isFile(path) and not exist:
                logging.warning(f"由于文件{path}已存在，自动跳过多线程下载！")
                self._result = "skip"
                return "skip"
            createDir(getFileDir(path))
            if exist and not force:
                path = getRepeatFileName(path)
            logging.info(f"正在多线程下载文件{url}到{path}！")
            response = requests.get(url, headers=header, stream=True, verify=False)
            total_size = int(response.headers.get('content-length', 1024))
            block_size = 1024
            progress = 0
            with open(path, "wb") as file:
                for chunk in response.iter_content(chunk_size=block_size):
                    if self._cancel:
                        logging.info(f"下载文件{url}到{path}被取消！")
                        self._result = "cancel"
                        file.close()
                        deleteFile(path)
                        return "cancel"
                    if chunk:
                        file.write(chunk)
                        progress += len(chunk)
                        self._progress = progress / total_size * 100
            logging.info(f"已将文件{url}多线程下载到{path}！")
            self._result = "success"
            return path
        except Exception as ex:
            deletePath(path)
            logging.error(f"多线程下载文件{url}到{path}失败，报错信息：{ex}！")
            self._result = "fail"
            return "fail"

    def download(self, url: str, path: str, manager: DownloadManager = None, exist: bool = True, force: bool = False, header: dict = REQUEST_HEADER):
        self.session = manager.downloadThreadPool.submit(self._download, url, path, exist, force, header)

    def cancel(self):
        """
        取消下载
        """
        self._cancel = True

    def progress(self):
        """
        下载进度
        :return: 0-100之间的小数进度
        """
        return self._progress

    def isFinished(self):
        """
        任务完成状态
        :return: 是否完成
        """
        if self._result is not None:
            return True
        else:
            return False

    def result(self):
        """
        任务结果
        :return: skip,cancel,success,fail
        """
        return self._result

    def outputPath(self):
        try:
            if self._result == "success":
                return self.session.result(0.1)
        except TimeoutError:
            return None


downloadManager = DownloadManager()
