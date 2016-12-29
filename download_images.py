#!/usr/bin/env python3

import json
import logging
import os
import shutil

from lib.DownloadManager import DownloadManager

logging.basicConfig(
    level=logging.INFO,
    format="%(name)s %(levelname)s: %(message)s"
)

# ---------
engine = "baidu"
input_path = "output/化验单/%s.json" % engine
input_path = "error.json"
# ---------

output_dir = os.path.join("images", engine)
error_log_dir = os.path.join("images", engine)

shutil.rmtree(output_dir, ignore_errors=True)
os.makedirs(output_dir, exist_ok=True)
os.makedirs(error_log_dir, exist_ok=True)

with open(input_path, "r", encoding="UTF-8") as fd:
    data = json.load(fd)

download_manager = DownloadManager(os.path.abspath(output_dir))

for (url, name) in data.items():
    download_manager.add_download_url(url, name)

result = download_manager.run(retry_with_curl=True)

error_urls = {r.url: r.path for r in result if r.error is not None}

with open("error.json", 'w', encoding='UTF-8') as fd:
    json.dump(error_urls, fd, indent=2, ensure_ascii=False)
