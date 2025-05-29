#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from ctypes import BigEndianStructure
import pendulum
from pathlib import Path
from config import config


from business.services.wechat_data_crawler import WechatDataFetcher
from business.services.wechat_data_process import WechatDataAnalyzer, WechatDataPublisher


def run(begin_date=None, end_date=None):
    # 下载所有数据
    if begin_date is not None:
        begin_date = pendulum.parse(begin_date)
    if end_date is not None:
        end_date = pendulum.parse(end_date)

    crawler = WechatDataFetcher(begin_date, end_date)
    download_info = crawler.download_all()
    account_name = download_info["account_name"]
    traffic_path, article_7d_path, article_detail_paths, user_growth_path = download_info["download_paths"]

    # 处理数据
    processor = WechatDataAnalyzer(account_name, traffic_path, article_7d_path, article_detail_paths, user_growth_path=user_growth_path)
    processor.process_data()

    # 发布数据
    publisher = WechatDataPublisher(account_name)
    publisher.publish()


def publish_wechat_data(account_name):
    """
    发布公众号数据到指定目录
    :param account_name:
    :return:
    """
    publisher = WechatDataPublisher(account_name)
    publisher.publish()
    return True

if __name__ == '__main__':
    run()