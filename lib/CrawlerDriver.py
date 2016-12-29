import logging
import os

from selenium import webdriver

import parsers


class CrawlerDriver:
    support_engines = {
        'baidu': parsers.BaiduParser,
        'bing': parsers.BingParser,
        '360': parsers.So360Parser,
        'google': parsers.GoogleParser
    }

    logger = logging.getLogger("CrawlerDriver")
    logger.setLevel(logging.INFO)

    def __init__(self):
        self._driver = None

    @property
    def driver(self):
        self.open_browser()
        return self._driver

    def open_browser(self, reopen: bool = False) -> None:
        """
        启动浏览器，若浏览器已启动，不做任何操作
        :param reopen: 强制开启新浏览器
        """
        if not reopen and self._driver is not None:
            return
        this_path = os.path.abspath(os.path.dirname(__file__))  # 本文件路径
        chrome_driver_path = os.path.join(this_path, '../driver/chromedriver')

        """
        配置Chrome driver (use 2.27)
        http://www.seleniumhq.org/docs/03_webdriver.jsp#chromedriver
        https://github.com/SeleniumHQ/selenium/wiki/ChromeDriver
        """
        self._driver = webdriver.Chrome(chrome_driver_path)

        # 最大化窗口，因为每一次爬取只能看到视窗内的图片
        self._driver.maximize_window()

    def parse_search_page(self, word: str, engine: str, size_type: str = None) -> dict:
        if engine not in CrawlerDriver.support_engines:
            CrawlerDriver.logger.error("engine %s is not supported", engine)
            return {}

        parser = CrawlerDriver.support_engines[engine](self.driver)
        if size_type is not None:
            parser.set_size_filter(size_type)
        CrawlerDriver.logger.info("parsing page...")
        img_dict = parser.get_images(word)
        logging.info("%s find %s photos" % (engine, parser.img_num))
        return img_dict
