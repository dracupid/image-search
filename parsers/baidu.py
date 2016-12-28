from .base_parser import Parser


class BaiduParser(Parser):
    size_map = {
        Parser.SUPER_LARGE: 9,
        Parser.LARGE: 3,
        Parser.MIDDLE: 2,
        Parser.SMALL: 1,
    }

    def set_size_filter(self, size_type):
        if size_type is None:
            return

        size_arg = BaiduParser.size_map[size_type]
        self.url_pattern += ("&z=%d" % size_arg)

    def __init__(self, driver):
        super().__init__("baidu", driver, xpath='//div[@id="imgid"]/div/ul/li',
                         url_pattern="http://image.baidu.com/search/index?tn=baiduimage&word=%s")

    def _parse(self):
        self.load_all_by_scroll(interval=0.1, repeat_threshold=30)

        for element in self.driver.find_elements_by_xpath(self.xpath):
            img_url = element.get_attribute('data-objurl')
            name = element.get_attribute('data-title')
            if name is not None:
                name = name.replace("<strong>", "").replace("</strong>", "")

            self._add_img(name, img_url)
