import os
import pandas as pd
from playwright.sync_api import sync_playwright
import random
from pathlib import Path
from config import config
from tools.locker import Locker
import pendulum
import re
import time
import shutil

from business.services.wechat_data_crawler import WechatDataFetcher
from business.services.wechat_data_process import WechatDataAnalyzer


def run():
    # 下载所有数据
    crawler = WechatDataFetcher()
    crawler.download_all()

    # 处理数据
    processor = WechatDataAnalyzer()
    processor.process_data()


if __name__ == '__main__':
    run()   