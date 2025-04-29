#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pendulum
from pathlib import Path
from config import config


from business.services.wechat_data_crawler import WechatDataFetcher
from business.services.wechat_data_process import WechatDataAnalyzer, WechatDataPublisher


def run():
    # 下载所有数据
    crawler = WechatDataFetcher()
    download_info = crawler.download_all()
    account_name = download_info["account_name"]
    traffic_path, article_7d_path, article_detail_paths, user_growth_path = download_info["download_paths"]

    # 处理数据
    processor = WechatDataAnalyzer(account_name, traffic_path, article_7d_path, article_detail_paths, user_growth_path=user_growth_path)
    processor.process_data()

    # 发布数据
    publisher = WechatDataPublisher(account_name)
    publisher.publish()


if __name__ == '__main__':
    run()