#!/usr/bin/env python3

import logging
import os
import shutil
import traceback
import urllib
import time
import urllib.request

import requests
from requests.packages.urllib3 import exceptions as urllib3_exceptions
from selenium import webdriver

import parsers
from concurrency import ConcurrencyRunner

THIS_PATH = os.path.abspath(os.path.dirname(__file__))  # 本文件路径
CHROME_DRIVER = os.path.join(THIS_PATH, 'driver/chromedriver')

# support_engines = {
#     'sogou': {'url': 'http://pic.sogou.com/pics?query=%s', 'parser': BaiduParser},
#     'baidu': {'url': 'http://image.baidu.com/search/index?tn=baiduimage&word=%s', 'parser': BaiduParser},
#     '360': {'url': 'http://image.so.com/i?q=%s', 'parser': BaiduParser},
#     'google': {'url': 'https://www.google.com/search?q=%s&tbm=isch', 'parser': BaiduParser},
#     'bing': {'url': 'http://www.bing.com/images/search?q=%s&FORM=IGRE', 'parser': BaiduParser},
#     'yahoo': {'url': 'https://sg.images.search.yahoo.com/search/images?p=%s', 'parser': BaiduParser}
# }

support_engines = {
    'baidu': parsers.BaiduParser,
    'bing': parsers.BingParser,
    '360': parsers.So360Parser,
    'google': parsers.GoogleParser
}


# def get_xpath_by_url(url):
#     """根据url确定搜索引擎,从而确定图片的正则匹配"""
#     substring = url[:url.index('/', len('https://'))]
#     _map = {
#         'sogou': '//div[@id="imgid"]/ul/li/a/img',
#         'baidu': '//div[@id="imgid"]/div/ul/li/div/a/img',
#         'so.com': '//div[@id="waterfallX"]/div/ul/li/a/img',  # 360搜索
#         'yahoo': '//div[@id="res-cont"]/section/div/ul/li/a/img',
#         'bing.com': '//div[@id="dg_c"]/div/div[@class="imgres"]/div/div/a/img',
#         'google': '//div[@id="ires"]/div/div[@id="isr_mc"]/div/div/div/div/a/img',
#     }
#     for k in _map.keys():
#         if k in substring:
#             return _map[k]
#     raise AssertionError(
#         'can only deal with %s, %s is not defined. you should add by yourself.' % (_map.keys(), substring))


def _download_image(url, file_path):
    if url.startswith('data:'):  # google或者百度图片有这种形式的图片,data:image/jpeg;开头
        urllib.request.urlretrieve(url, file_path)
        return
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_3) AppleWebKit/537.36 (KHTML, like Gecko) ' +
                      'Chrome/55.0.2883.95 Safari/537.36',
        'Connection': 'close',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8'

    }
    r = requests.get(url, headers=headers, stream=True, timeout=8, allow_redirects=True)
    with open(file_path, 'wb') as f_write:
        f_write.write(r.raw.read())


def download_item(url, file_path, max_retry=1):
    logger = logging.getLogger("crawler")
    logger.setLevel(logging.INFO)
    logger.debug('%s -> %s', url, file_path)
    is_error = False

    try_time = 0
    skip_retry = False

    result = (True, )

    while try_time < max_retry:
        if try_time > 0:
            logger.warning("retry %s #%d", url, try_time)
        else:
            time.sleep(1)  # 停1s后重试
        try:
            _download_image(url, file_path)  # 保存图片
        except requests.exceptions.RequestException as e:
            is_error = True
            logger.error('failed to fetch %s %s', url, e)
        except urllib3_exceptions.ReadTimeoutError:
            is_error = True
            skip_retry = True
            logger.error('timeout to fetch %s', url)
        except urllib3_exceptions.ProtocolError as e:
            is_error = True
            logger.error('failed to fetch %s %s', url, e)
        except:
            is_error = True
            skip_retry = True
            logging.error(traceback.format_exc())
            logger.error('failed to save %s', url)
        finally:
            if is_error:
                try:
                    os.remove(file_path)
                    result = (False, url, file_path)
                except:
                    pass
                if skip_retry:
                    break
                try_time += 1
            else:
                result = (True,)
                break
    return result

def download_item_process(item):
    (url, file_path) = item
    return download_item(url, file_path)


def download_by_word(word, output_dir="./output", engines=('baidu',), concurrency=True, size_type=None):
    """
    根据关键词和指定的搜索引擎抓取图片
    :param word: 关键词
    :param output_dir: 输出目录
    :param engines: 搜索引擎列表
    :param concurrency: 是否并发下载
    :param size_type: 尺寸
    """

    engines = map(lambda x: x.lower(), engines)

    """
    配置Chrome driver (2.27)
    http://www.seleniumhq.org/docs/03_webdriver.jsp#chromedriver
    https://github.com/SeleniumHQ/selenium/wiki/ChromeDriver
    """
    driver = webdriver.Chrome(CHROME_DRIVER)
    # 最大化窗口，因为每一次爬取只能看到视窗内的图片
    driver.maximize_window()

    img_items = []

    shutil.rmtree(output_dir, ignore_errors=True)
    os.makedirs(output_dir, exist_ok=True)  # 确保文件夹存在

    for engine in engines:
        if engine not in support_engines:
            logging.error("engine %s is not supported", engine)
            continue

        parser = support_engines[engine](driver)
        if size_type is not None:
            parser.set_size_filter(size_type)
        img_dict = parser.get_images(word)

        logging.info("%s find %s photos" % (engine, len(img_dict)))

        img_items += img_dict.items()

    img_items = list(map(lambda item: (item[0], os.path.join(output_dir, item[1])), img_items))
    # 下载图片
    logging.info("start to download")
    if concurrency:
        ConcurrencyRunner(download_item_process, img_items, process_num=1, thread_per_process=4).run()
    else:
        for url, file_path in img_items:
            download_item(url, file_path)
