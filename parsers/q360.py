from urllib import parse

from .base_parser import Parser


class So360Parser(Parser):
    size_map = {
        Parser.SUPER_LARGE: 1,
        Parser.LARGE: 4,
        Parser.MIDDLE: 2,
        Parser.SMALL: 3,
    }

    def set_size_filter(self, size_type):
        if size_type is None:
            return

        size_arg = So360Parser.size_map[size_type]
        self.url_pattern += ("&zoom=%d" % size_arg)

    def __init__(self, driver):
        super().__init__("360", driver, xpath='//ul[@class="wfx_row"]/li[not(@class="commercialCell")]',
                         url_pattern="http://image.so.com/i?q=%s")

    def _parse(self):
        # interval = 0.2
        def cb():
            for element in self.driver.find_elements_by_xpath(self.xpath):
                img_ele = element.find_element_by_xpath(".//a/img")
                if img_ele is None:
                    continue
                img_url = parse.unquote(img_ele.get_attribute('data-originalsrc'))
                name = element.find_element_by_xpath('.//a[@class="img_link"]').get_attribute('title')
                print(img_url + " -> " + name)
                self._add_img(name, img_url)

        self.load_all_by_scroll(interval=0.1, repeat_threshold=10, load_more_btn_class="btn_loadmore", cb=cb,
                                step=self.window_height * 0.6)
