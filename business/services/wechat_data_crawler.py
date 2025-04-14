#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
    此文件的主要功能是爬取微信公众号运营数据，并将数据保存为Excel文件。
    具体步骤为：
    1. 打开微信公众号后台登录页面，展示登录二维码。等待用户扫码登录。
    2. 登录成功后，在页面中找到账号名称，并获取账号名称。
    3. 获取内容分析数据
        3.1 在左侧导航栏，展开“数据分析”菜单，点击“内容分析”，找到“下载数据明细”链接，点击下载账号维度的运营数据。
        3.2 点击“内容分析”页面顶部的tab：已通知内容，然后点击”下载数据明细“，该数据是以文章为维度，统计文章发表后7日内的数据。
        3.3 在“已通知内容“页面，点击”详情“，进入到文章详情页面，点击”下载数据明细“，该数据是处理特定文章的运营数据。

        注意，
        1）以上下载的数据都要先放到datas/tmp目录下，然后再进行处理。
        2）处理完之后，需要清理datas/tmp目录下的文件。
    4. 处理datas/tmp目录下的文件
        4.1 根据账号名称，检查datas/wechat_operation_data/账号名称目录是否存在，如果不存在，则创建该目录。
        4.2 处理完之后的数据，更新到datas/wechat_operation_data/账号名称 目录下
"""

import os
import pandas as pd
from playwright.sync_api import sync_playwright
import random
from pathlib import Path
from config import config


class WechatDataFetcher:
    def __init__(self):
        self.browser = None
        self.page = None
        self.tmp_data_dir = Path(config.root_dir) / 'tmp/data/wechat'

    def login(self, remenber=True):
        session_dir = Path(config.root_dir) / 'tmp/session/wechat/'
        if not session_dir.exists():
            session_dir.mkdir(parents=True)
        session_path = session_dir / 'wechat_session.json'

        # 确保self.tmp_data_dir存在
        if not self.tmp_data_dir.exists():
            self.tmp_data_dir.mkdir(parents=True)
        
        # 定义通用的浏览器配置和headers
        user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3',
            'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:54.0) Gecko/20100101 Firefox/54.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36'
        ]
        
        with sync_playwright() as p:
            self.browser = p.chromium.launch(headless=False, downloads_path=self.tmp_data_dir)
            headers = {'User-Agent': random.choice(user_agents)}
            self.page = self.browser.new_page(extra_http_headers=headers)
            
            if remenber and os.path.exists(session_path):
                self.page.context.storage_state(path=session_path)
            
            self.page.goto('https://mp.weixin.qq.com/')
            print('请扫码登录微信公众号后台...')
            self.page.wait_for_url('https://mp.weixin.qq.com/*')
            if remenber:
                self.page.context.storage_state(path=session_path)

            # 等待导航栏加载完成
            self.page.wait_for_selector('#js_index_menu')
                
            # 模拟人类操作行为
            time.sleep(random.uniform(0.5, 3))
            scroll_distance = random.randint(100, 500)
            self.page.evaluate(f'window.scrollBy(0, {scroll_distance});')
                
    def get_account_name(self):
        """
        账号名称在导航栏最下方
        """
        self.page.wait_for_selector('div.account_box-body > span.acount_box-nickname')
        account_name = self.page.text_content('div.account_box-body > span.acount_box-nickname')
        return account_name.strip()

    def download_account_articles_data(self):
        self.page.click('text=数据分析')
        # 随机等待
        time.sleep(random.uniform(0.5, 3))
        # 随机滚动
        scroll_distance = random.randint(100, 500)
        self.page.evaluate(f'window.scrollBy(0, {scroll_distance});')

        self.page.click('text=内容分析')
        # 随机等待
        time.sleep(random.uniform(0.5, 3))
        # 随机滚动
        scroll_distance = random.randint(100, 500)
        self.page.evaluate(f'window.scrollBy(0, {scroll_distance});')

        # 确保下载链接可见并点击
        download_link = self.page.wait_for_selector('text=下载数据明细', state='visible')
        self.page.evaluate('element => element.scrollIntoView()', download_link)
        time.sleep(random.uniform(0.5, 2))  # 随机等待确保元素完全可见
        download_link.click()
        self._wait_for_download()

    def download_article_7d_data(self):
        self.page.click('text=已通知内容')
        # 随机等待
        time.sleep(random.uniform(0.5, 3))
        # 随机滚动
        scroll_distance = random.randint(100, 500)
        self.page.evaluate(f'window.scrollBy(0, {scroll_distance});')
        # 随机点击
        clickable_elements = self.page.query_selector_all('button, a')
        if clickable_elements:
            random_element = random.choice(clickable_elements)
            random_element.click(force=True)
            time.sleep(random.uniform(0.5, 3))
        self.page.click('text=下载数据明细')
        self._wait_for_download('datas/tmp/article_7d_data.xlsx')

    def download_specific_article_data(self):
        self.page.click('text=详情')
        # 随机等待
        time.sleep(random.uniform(0.5, 3))
        # 随机滚动
        scroll_distance = random.randint(100, 500)
        self.page.evaluate(f'window.scrollBy(0, {scroll_distance});')
        # 随机点击
        clickable_elements = self.page.query_selector_all('button, a')
        if clickable_elements:
            random_element = random.choice(clickable_elements)
            random_element.click(force=True)
            time.sleep(random.uniform(0.5, 3))
        self.page.click('text=下载数据明细')
        self._wait_for_download('datas/tmp/specific_article_data.xlsx')

    def _wait_for_download(self, path):
        while not os.path.exists(path):
            pass


class WechatDataAnalyzer:
    def __init__(self, account_name):
        self.account_name = account_name
        self.data_dir = f'datas/wechat_operation_data/{self.account_name}'
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)

    def process_data(self):
        tmp_dir = 'datas/tmp'
        for file in os.listdir(tmp_dir):
            if file.endswith('.xlsx'):
                file_path = os.path.join(tmp_dir, file)
                df = pd.read_excel(file_path)
                # 这里可以添加具体的数据处理逻辑
                new_file_path = os.path.join(self.data_dir, file)
                df.to_excel(new_file_path, index=False)

        self._clean_tmp_dir()

    def _clean_tmp_dir(self):
        tmp_dir = 'datas/tmp'
        for file in os.listdir(tmp_dir):
            file_path = os.path.join(tmp_dir, file)
            os.remove(file_path)


class WechatDataPipeline:
    def __init__(self):
        self.fetcher = WechatDataFetcher()
        self.analyzer = None

    def login(self):
        self.fetcher.login()
        return self

    def get_account_name(self):
        account_name = self.fetcher.get_account_name()
        self.analyzer = WechatDataAnalyzer(account_name)
        return self

    def download_all_data(self):
        self.fetcher.download_account_data()
        self.fetcher.download_article_7d_data()
        self.fetcher.download_specific_article_data()
        self.fetcher.browser.close()
        return self

    def process_data(self):
        self.analyzer.process_data()
        return self


if __name__ == '__main__':
    pipeline = WechatDataPipeline()
    pipeline.login().get_account_name().download_all_data().process_data()