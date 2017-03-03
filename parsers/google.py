import json

from .base_parser import Parser


class GoogleParser(Parser):
    size_map = {
        Parser.SUPER_LARGE: "isz%%3Al",
        Parser.LARGE: "isz%%3Al",
        Parser.MIDDLE: "isz%%3Am",
        Parser.SMALL: None,
    }

    def set_size_filter(self, size_type):
        if size_type is None:
            return

        size_arg = GoogleParser.size_map[size_type]
        if size_arg is not None:
            self.url_pattern += ("&tbs=%s" % size_arg)

    def __init__(self, driver):
        super().__init__("google", driver, xpath='//div[@id="rg_s"]/div/div[@class="rg_meta"]',
                         url_pattern="https://www.google.com/search?q=%s&tbm=isch")

    def _parse(self):
        self.load_all_by_scroll(interval=0.2, repeat_threshold=10, load_more_btn_class="ksb _kvc")

        for element in self.driver.find_elements_by_xpath(self.xpath):
            info = json.loads(element.get_attribute('innerText'))
            img_url = info["ou"]
            name = info["s"]
            self._add_img(name, img_url)
