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
import pendulum
import re
import time

class WechatDataFetcher:

    def __init__(self, p, begin_date=None, end_date=None):
        self.browser = None
        self.page = None
        self.p = p
        if begin_date is None:
            self.begin_date = pendulum.now() - pendulum.duration(days=30)  # 最多2个月的数据
        else:
            self.begin_date = begin_date
        if end_date is None:
            self.end_date = pendulum.now() - pendulum.duration(days=1)
        else:
            self.end_date = end_date
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
        
        self.browser = self.p.chromium.launch(headless=False, downloads_path=self.tmp_data_dir)
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
        print(account_name)
        return account_name.strip()

    def download_traffic_data(self):
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
        # 定位第一个"下载数据明细"超链接，必须等待元素出现
        self.page.wait_for_selector('text=下载数据明细')
        download_links = self.page.query_selector_all('text=下载数据明细')
        first_download_link = download_links[0]
        # 滑动到第一个元素使其可见
        self.page.evaluate('element => element.scrollIntoView()', first_download_link)
        # 等待元素可见
        self.page.wait_for_selector('text=下载数据明细', state='visible')
        time.sleep(random.uniform(0.5, 2))  # 随机等待确保元素完全可见

        print(self.begin_date.strftime('%Y-%m-%d'), self.end_date.strftime('%Y-%m-%d'))
        # 根据self.begin_date和self.end_date来选择下载的日期范围
        _pick_date(self.begin_date, self.end_date, self.page, self.page.query_selector('//form[@class="mass_all_filter"]'))
        self._wait_for_download(lambda: first_download_link.click(), self.tmp_data_dir / 'traffic_data.xlsx')

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
        self._wait_for_download(lambda: self.page.click('text=下载数据明细'), self.tmp_data_dir / 'article_7d_data.xlsx')

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
            pendulum.sleep(random.uniform(0.5, 3))
        self._wait_for_download(lambda: self.page.click('text=下载数据明细'), self.tmp_data_dir / 'specific_article_data.xlsx')
        
    def _wait_for_download(self, click_action, path=None, timeout=60):
        with self.page.expect_download() as download_info:
            click_action()
        download = download_info.value
        if path is None:
            path = self.tmp_data_dir / download.suggested_filename
        download.save_as(path)
        # 轮询检查文件是否下载完成
        start_time = pendulum.now()
        while not path.exists():
            if (pendulum.now() - start_time).total_seconds() > timeout:
                raise TimeoutError('文件下载超时')
            pendulum.sleep(1)


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

    def __init__(self, begin_date=None, end_date=None):
        self.analyzer = None
        self.p = sync_playwright().start()
        self.fetcher = WechatDataFetcher(self.p, begin_date, end_date)

    def login(self):
        self.fetcher.login()
        return self

    def get_account_name(self):
        account_name = self.fetcher.get_account_name()
        self.analyzer = WechatDataAnalyzer(account_name)
        return self

    def download_all_data(self):
        self.fetcher.download_traffic_data()
        self.fetcher.download_article_7d_data()
        #self.fetcher.download_specific_article_data()
        self.fetcher.browser.close()
        return self

    def process_data(self):
        self.analyzer.process_data()
        return self


def _pick_date(begin: pendulum.DateTime, end: pendulum.DateTime, page, parent):
    """
    需要确保日期选择器在页面上显示
    微信后台日期选择器，选择特定的日期范围。
    跨度不能超过2个月
    """
    # 如果end - begin超过 2各月，throw exception
    if begin > end:
        raise ValueError("开始日期不能大于结束日期")
    if end >= pendulum.today():
        raise ValueError("结束日期必须早于今日")
    delta = pendulum.Interval(begin, end)
    if delta.in_months() >= 2:
        raise ValueError("日期选择器超出范围，开始结束时间相差不能超过2个月")

    def _abstract_year_month(date_str: str):
        match = re.search(r"(\d{4})年\s+(\d{1,2})月", date_str)
        if not match:
            raise ValueError("日历标题日期格式错误")
        return int(match.group(1)), int(match.group(2))

    # 打开日期选择器
    picker_icon = parent.query_selector(
        '//span[@class="weui-desktop-picker__icon-wrap"]'
    )
    picker_icon.click()
    page.wait_for_timeout(1000)

    pannels = parent.query_selector_all(
        '//dd[contains(@class, "weui-desktop-picker__dd")]/div[contains(@class, "weui-desktop-picker__panel_day")]'
    )
    if len(pannels) < 2:
        raise ValueError("日历面板数量错误")
    left_pannel, right_pannel, *_ = pannels

    left_head = left_pannel.query_selector(
        '//div[contains(@class, "weui-desktop-picker__panel__hd")]'
    )
    right_head = right_pannel.query_selector(
        '//div[contains(@class, "weui-desktop-picker__panel__hd")]'
    )

    # 选择begin
    # 判断是否进行日期翻页，计算点击 < or > 按钮的次数，并点击获取指定日期范围的日历
    # 如果begin小于left pannel head日期,需要向左翻页
    left_year, left_month = _abstract_year_month(left_head.inner_text())
    left_min_day = pendulum.date(left_year, left_month, 1)
    begin_delta = pendulum.Interval(left_min_day, pendulum.date(begin.year, begin.month, 1))
    left_delta_month = begin_delta.in_months()
    if left_delta_month < 0:
        for i in range(abs(left_delta_month)):
            left_pannel.query_selector("button").click()
            page.wait_for_timeout(500)
    # 如果begin大于righ pannel head日期，需要向右翻页
    if left_delta_month >= 2:
        for i in range(left_delta_month):
            right_pannel.query_selector("button").click()
            page.wait_for_timeout(500)

    # 定位begin对应的日期，点击
    _, left_month = _abstract_year_month(left_head.inner_text())
    (
        _,
        right_month,
    ) = _abstract_year_month(right_head.inner_text())
    pannel = left_pannel if left_month == begin.month else right_pannel
    pannel.query_selector(
        f'//tbody//*//a[not(contains(@class, "weui-desktop-picker__faded")) and text()={begin.day}]'
    ).click()

    # 选择end
    right_year, right_month = _abstract_year_month(right_head.inner_text())
    right_min_day = pendulum.date(right_year, right_month, 1)
    end_delta = pendulum.Interval(right_min_day, pendulum.date(end.year, end.month, 1))
    right_delta_month = end_delta.in_months()
    if right_delta_month > 0:
        for i in range(right_delta_month):
            right_pannel.query_selector("button").click()
            page.wait_for_timeout(500)
    # 定位end对应的日期，点击
    _, left_month = _abstract_year_month(left_head.inner_text())
    (
        _,
        right_month,
    ) = _abstract_year_month(right_head.inner_text())
    pannel = left_pannel if left_month == end.month else right_pannel
    pannel.query_selector(
        f'//tbody//*//a[not(contains(@class, "weui-desktop-picker__faded")) and text()={end.day}]'
    ).click()

    # 关闭picker
    picker_icon.click()



def run():
    pipeline = WechatDataPipeline()
    pipeline.login().get_account_name().download_all_data().process_data()


if __name__ == '__main__':
    run()