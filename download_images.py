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
word = "化验单"
engine = ("baidu", "bing", "360", "google")
input_path_list = ["output/%s/%s.json" % (word, e) for e in engine]
# ---------

output_dir = os.path.join("images")
log_dir = os.path.join("log")

shutil.rmtree(output_dir, ignore_errors=True)
os.makedirs(output_dir, exist_ok=True)
os.makedirs(log_dir, exist_ok=True)

all_urls = {}

# 读取并合并数据
for input_path in input_path_list:
    with open(input_path, "r", encoding="UTF-8") as fd:
        data = json.load(fd)
        all_urls.update(data)

# 输出所有连接
print("=> total: %s" % len(all_urls))
with open(os.path.join(log_dir, "all.json"), 'w', encoding='UTF-8') as fd:
    json.dump(all_urls, fd, indent=2, ensure_ascii=False)

# 下载
download_manager = DownloadManager(os.path.abspath(output_dir))

for (url, name) in all_urls.items():
    download_manager.add_download_url(url, name)

result = download_manager.run(retry_with_curl=True)

error_urls = {r.url: r.path for r in result if r.error is not None}

print("=> error: %s" % len(error_urls))
with open(os.path.join(log_dir, "err.json"), 'w', encoding='UTF-8') as fd:
    json.dump(error_urls, fd, indent=2, ensure_ascii=False)
