#!/usr/bin/env python3

import logging

from main import download_by_word
from parsers import Parser

if __name__ == '__main__':
    logging.basicConfig(
        level=logging.INFO,
        format="%(name)s %(levelname)s: %(message)s"
    )

    logging.getLogger("requests.packages.urllib3.connectionpool").setLevel(logging.WARN)

    download_by_word("化验单", engines=("baidu",), size_type=Parser.LARGE, output_dir="./output_baidu")
