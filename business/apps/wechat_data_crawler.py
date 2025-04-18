#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pendulum


from business.services.wechat_data_crawler import WechatDataFetcher
from business.services.wechat_data_process import WechatDataAnalyzer


def run():
    # 下载所有数据
    crawler = WechatDataFetcher()
    download_info = crawler.download_all()
    account_name = download_info["account_name"]
    traffic_path, article_7d_path, article_detail_paths = download_info["download_paths"]

    # 处理数据
    processor = WechatDataAnalyzer(account_name, traffic_path, article_7d_path, article_detail_paths)
    processor.process_data()


if __name__ == '__main__':
    run()   