#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pendulum
from pathlib import Path
from config import config


from business.services.wechat_data_crawler import WechatDataFetcher
from business.services.wechat_data_process import WechatDataAnalyzer


def run():
    # 下载所有数据
    #crawler = WechatDataFetcher()
    #download_info = crawler.download_all()
    #account_name = download_info["account_name"]
    #traffic_path, article_7d_path, article_detail_paths = download_info["download_paths"]

    # 测试数据
    account_name = "子君昭穆"
    traffic_path = Path(config.root_dir) / "tmp/data/wechat/traffic_data.xlsx"
    article_7d_path = Path(config.root_dir) / "tmp/data/wechat/article_7d_data.xlsx"
    article_detail_paths = [
        Path(config.root_dir) / "tmp/data/wechat/历史上人们改姓原因千千万，但这3家貌似改的也太随便了点。.xlsx",
        Path(config.root_dir) / "tmp/data/wechat/如今的中国人中还有匈奴后裔吗？.xlsx",
        Path(config.root_dir) / "tmp/data/wechat/真靠谱吗？广东竟然生活着两支鲜卑皇族后裔.xlsx",
    ]

    # 处理数据
    processor = WechatDataAnalyzer(account_name, traffic_path, article_7d_path, article_detail_paths)
    processor.process_data()


if __name__ == '__main__':
    run()   