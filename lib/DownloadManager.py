import logging
import os
import traceback
import urllib
import urllib.request
from typing import List
from urllib.parse import urlparse

import requests
from requests.packages.urllib3 import exceptions as urllib3_exceptions

from lib.MultiThreadRunner import MultiThreadMapper


def _resolve_ext(url):
    """
    根据URL解析文件扩展名
    :param url: url
    :return: 扩展名，如 '.jpg'
    """
    return os.path.splitext(urlparse(url).path)[1] or ".jpg"


def format_connection_error(e):
    e_str = str(e).strip()

    if "[Errno" in e_str:
        start = e_str.index("[Errno")
        return e_str[start:-4]
    else:
        e_str = e_str[1:-1]
        return e_str


class DownloadResult:
    def __init__(self, url: str, path: str, error: Exception = None):
        self.url = url
        self.path = path
        self.error = error


class DownloadManager:
    def __init__(self, output_path: str, concurrency: int = 8):
        self.download_queue = []
        self.num = 0
        self.output_path = output_path  # type: List[DownloadResult]
        self.concurrency = concurrency
        logging.getLogger("requests.packages.urllib3.connectionpool").setLevel(logging.WARN)
        self.logger = logging.getLogger("DM")
        self.logger.setLevel(logging.WARN)

    def add_download_url(self, url: str, name: str):
        """
        向队列中添加下载请求
        :param url: url
        :param name: 文件名
        """
        if url.startswith('data:image/jpeg'):
            extname = ".jpg"
        elif url.startswith('data:image/gif'):
            extname = ".gif"
        elif url.startswith('data:image/png'):
            extname = ".png"
        else:
            extname = _resolve_ext(url)
        self.download_queue.append({
            "index": self.num,
            "url": url,
            "path": os.path.join(self.output_path, name.rstrip(extname) + extname).lower()
        })
        self.num += 1

    def cleanup(self):
        """
        清空下载队列
        """
        self.num = 0
        self.download_queue = []

    def download_curl(self, url: str, file_path: str) -> DownloadResult:
        cmd = "curl '%s' -sSL --connect-timeout 5 > '%s'" % (url, file_path)
        self.logger.warning("retry by " + cmd + "\n")
        code = os.system(cmd)
        self.logger.warning("exit %d" % code)
        if code == 0:
            return DownloadResult(url, file_path)
        else:
            try:
                os.remove(file_path)
            except FileNotFoundError:
                pass
            return DownloadResult(url, file_path, Exception("curl failed"))

    def download(self, url: str, file_path: str, timeout: int = 8) -> DownloadResult:
        """
        下载图片
        :param url: URL
        :param file_path: 文件路径
        :param timeout: 超时秒数
        """
        self.logger.info('%s -> %s', url, file_path)

        if url.startswith('data:'):
            urllib.request.urlretrieve(url, file_path)
            return DownloadResult(url, file_path)

        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_3) AppleWebKit/537.36 (KHTML, like Gecko) ' +
                          'Chrome/55.0.2883.95 Safari/537.36',
            'Connection': 'close'
        }

        error = None

        ## 下载大文件的时候怎么设置超时
        try:
            try:
                r = requests.get(url, headers=headers, stream=True, timeout=timeout, allow_redirects=True)
                with open(file_path, 'wb') as fd:
                    fd.write(r.raw.read())
            except Exception as e:
                error = e
                raise e
        except requests.ConnectTimeout:
            self.logger.error('ConnectTimeout -> %s', url)
        except requests.ConnectionError as e:
            self.logger.error('ConnectionError -> %s\n\t%s', url, format_connection_error(e))
        except requests.RequestException as e:
            self.logger.error('RequestException -> %s\n\t%s', url, e)
        except urllib3_exceptions.ReadTimeoutError:
            self.logger.error('ReadTimeout -> %s', url)
        except urllib3_exceptions.ProtocolError as e:
            self.logger.error('ProtocolError -> %s\n\t%s', url, e)
        except Exception:
            self.logger.error(traceback.format_exc())
            self.logger.error('failed to save %s', url)
        finally:
            if error is not None:
                try:
                    os.remove(file_path)
                except FileNotFoundError:
                    pass
                finally:
                    return DownloadResult(url, file_path, error)
            else:
                return DownloadResult(url, file_path)

    def map_fun(self, item: dict) -> DownloadResult:  # TODO: download
        return self.download(item["url"], item["path"])

    def run(self, retry_with_curl=False) -> List[DownloadResult]:
        """
        开始下载
        :return: 下载结果
        """
        if self.concurrency > 1:
            mapper = MultiThreadMapper(self.map_fun, self.download_queue)
            res = mapper.run(thread_per_process=self.concurrency)
        else:
            res = map(self.map_fun, self.download_queue)

        if retry_with_curl:
            res = map(lambda r: r if r.error is None else self.download_curl(r.url, r.path), res)

        self.cleanup()
        return res
