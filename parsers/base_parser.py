import math
import time
from abc import ABCMeta, abstractmethod


class Parser(metaclass=ABCMeta):
    SUPER_LARGE = 'super_large'
    LARGE = 'large'
    MIDDLE = 'middle'
    SMALL = 'small'

    def __init__(self, engine_name, driver, xpath, url_pattern):
        self.engine_name = engine_name
        self.driver = driver
        self.xpath = xpath
        self.img_dict = dict()
        self.img_num = 0
        self.url_pattern = url_pattern
        self.window_height = self.driver.execute_script("return window.innerHeight")

    def _open_url(self, word):
        """
        打开搜索引擎URL
        :param word: 关键词
        """
        url = self.url_pattern % (word,)
        # 浏览器打开要爬取的页面
        self.driver.get(url)

    @abstractmethod
    def _parse(self):
        """
        解析页面，获取所有图片的{URL: filename}，子类需要重写
        """
        pass

    @abstractmethod
    def set_size_filter(self, size_type):
        """
        设置图片大小过滤条件
        :param size_type: 尺寸
        """
        pass

    def get_images(self, word):
        """
        图片抓取主函数
        :param word: 关键词
        :return: 所有图片的{URL: filename} 字典
        """
        self.img_dict.clear()
        self._open_url(word)
        self._parse()
        return self.img_dict

    # def filter(self):
    #     pass

    def _add_img(self, name, url):
        """
        向字典中添加图片
        :param name:
        :param url:
        :return:
        """
        if url and url not in self.img_dict:
            suffix = url.split(".")[-1]
            if len(suffix) > 4:
                suffix = "jpg"
            name = "%s_%d_%s.%s" % (self.engine_name, self.img_num, name, suffix.lower())
            name = name.replace("/", "_").replace(" ", "_")
            self.img_num += 1
            self.img_dict[url] = name
            # print("ADD: " + name + " -> ", url)

    def load_all_by_scroll(self, interval=0, repeat_threshold=15, step=-1, load_more_btn_class=None):
        """
        滑动页面到底部
        """
        if step == -1:
            step = math.floor(self.window_height * 0.7)
        repeat_time = 0
        pos = step  # 滚动条位置,模拟滚动窗口以浏览下载更多图片
        last_pos = 0
        selector = None

        if load_more_btn_class is not None:
            selector = "document.getElementsByClassName('%s')" % (load_more_btn_class,)

        while True:
            # 处理单页内加载按钮的情况
            if load_more_btn_class:
                has_load_more = True if self.driver.execute_script("return %s.length" % (selector,)) == 1 else False
                if has_load_more:
                    self.driver.execute_script(selector + "[0].click()")

                print(has_load_more)

            self.driver.execute_script("document.body.scrollTop=%d" % pos)
            if interval > 0:
                time.sleep(interval)
            cur_pos = self.driver.execute_script('return document.body.scrollTop')
            print(pos, cur_pos)
            # 判断什么时候滑到底部
            if cur_pos == last_pos:  # 页面未能向下滑动
                repeat_time += 1
            else:
                repeat_time = 0
                pos += step  # 每次下滚500px

            last_pos = cur_pos
            if repeat_time > repeat_threshold:
                break
        print("load done")
