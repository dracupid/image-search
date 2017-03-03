#!/usr/bin/env python3
import json
import logging
import os

from lib.CrawlerDriver import CrawlerDriver
from parsers import Parser

# ---------
engine = "google"
word = "化验单"
# ---------

output_dir = os.path.join("output", word)
output_file = os.path.join(output_dir, engine + ".json")

os.makedirs(output_dir, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(name)s %(levelname)s: %(message)s"
)
logging.getLogger("requests.packages.urllib3.connectionpool").setLevel(logging.WARN)

crawler_driver = CrawlerDriver()
result = crawler_driver.parse_search_page(word, engine, Parser.LARGE)

with open(output_file, 'w', encoding='UTF-8') as fd:
    json.dump(result, fd, indent=2, ensure_ascii=False)
