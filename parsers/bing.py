import re

from .base_parser import Parser


class BingParser(Parser):
    size_map = {
        Parser.SUPER_LARGE: '+filterui:imagesize-wallpaper',
        Parser.LARGE: '+filterui:imagesize-large',
        Parser.MIDDLE: '+filterui:imagesize-medium',
        Parser.SMALL: '+filterui:imagesize-small',
    }

    def set_size_filter(self, size_type):
        if size_type is None:
            return

        size_arg = BingParser.size_map[size_type]
        self.url_pattern += ("&qft=%s" % size_arg)

    def __init__(self, driver):
        super().__init__("bing", driver, xpath='//div[@class="dg_u"]/div/a',
                         url_pattern="http://www.bing.com/images/search?q=%s")

    def _parse(self):
        self.load_all_by_scroll(interval=0.3, repeat_threshold=3, step=800, load_more_btn_class="btn_seemore")

        for element in self.driver.find_elements_by_xpath(self.xpath):
            img_info = element.get_attribute('m')
            m = re.search('imgurl:"([^"]*)"', img_info)

            if m is None:
                continue

            img_url = m.group(0)[8:-1]
            name = element.get_attribute('t1')

            self._add_img(name, img_url)
