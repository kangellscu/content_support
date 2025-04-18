#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
    此文件的主要功能是爬取微信公众号运营数据,并将数据保存为Excel文件。
    具体步骤为：
    1. 打开微信公众号后台登录页面，展示登录二维码。等待用户扫码登录。
    2. 登录成功后，在页面中找到账号名称，并获取账号名称。
    3. 下载内容分析数据
        3.1 流量分析数据
            描述: 按日,分渠道汇总账号的 日期|阅读次数|阅读人数|分享次数|分享人数|阅读原文次数|阅读原文人数|收藏次数|收藏人数|群发篇|渠道
            时效: 因为以日为维度, 数据一旦生成, 就不会变化。           
            操作: 在左侧导航栏，展开“数据分析”菜单，点击“内容分析”，找到“下载数据明细”链接，点击下载账号维度的运营数据。
            字段说明:
                分享次数: 用户转发或分享到好友会话、群聊、朋友圈及点击朋友"爱心"的次数
        3.2 已通知内容数据
            描述: 按文章维度汇总账号的 发表时间|总阅读人数|总阅读次数|总分享人数|分享次数|阅读后关注人数|送达人数|公众号消息阅读次数|送达阅读率|首次分享次数|分享产生阅读次数|首次分享率|首次分享带来阅读次数|阅读完成率|内容url
            时效: 因为以文章为维度, 数据会随着时间的推移而变化, 单篇文章发表7日后, 就不会更新了。
            操作: 点击“内容分析”页面顶部的tab:已通知内容,然后点击”下载数据明细“,该数据是以文章为维度,统计文章发表后7日内的数据。
            字段说明:
                阅读后关注人数: 阅读本篇发表后，通过官方途径，进入公众号主页关注的用户数
                送达阅读率: 公众号消息的阅读次数/消息群发送达的人数
                阅读完成率: 阅读完成该图文的人数/阅读该图文总人数
        3.3 单篇文章详情数据
            描述: 按文章维度汇总账号数据, 其中包含多个表, 如下:
                数据概况: 阅读次数|平均停留时长(s)|完读率|阅读后关注人数|分享次数|在看次数|点赞次数|赞赏(分)|评论(条)|互动率
                阅读转化: 送达人数|公众号消息阅读次数|首次分享次数|总分享次数|分享产生的阅读次数
                推荐转化: 曝光次数|阅读次数|关注人数
                数据趋势明细: 日期|传播渠道|阅读人数|阅读次数|分享人数|分享次数
                性别分布: 性别|人数|占比
                年龄分布: 年龄|人数|占比
                地域分布: 省份/直辖市|人数|占比
            时效: 数据会随着时间的推移而变化, 单篇文章发表30日后, 就不会更新了。注意: 数据趋势明细已有的日期数据不会更新, 只会新增日期数据。             
            操作: 在“已通知内容“页面, 点击”详情“, 进入到文章详情页面, 点击”下载数据明细“, 该数据是处理特定文章的运营数据。
            字段说明:
                送达人数: 内容群发时，送达的人数 
                公众号消息阅读次数: 内容在公众号会话及公众号列表的阅读次数
                首次分享次数: 用户在公众号会话及公众号列表阅读完后，转发或分享到好友会话、群聊、朋友圈及点击朋友“爱心”的次数，不包括非粉丝的点击
                总分享次数: 用户转发或分享到好友会话、群聊、朋友圈及点击朋友“爱心”的次数，包括非粉丝的点击
                分享产生的阅读次数: 由用户分享带来的阅读次数，即阅读来源为好友会话、群聊、朋友圈、朋友“爱心”的阅读次数
                曝光次数: 内容在公众号推荐场景出现的次数
                阅读次数: 内容在公众号推荐场景的阅读次数
                阅读率: 阅读次数/曝光次数
                读后关注次数: 用户在公众号推荐场景看完内容后关注的次数
                读后关注率: 读后关注次数/阅读次数
                分享次数: 在不同传播渠道中，转发或分享到好友会话、群聊、朋友圈及点击朋友“爱心"的人数及次数

        注意，
        1) 以上下载的数据都要先放到tmp/data/wechat目录下,然后再进行处理。
        2) 每次下载前,需要清理tmp/data/wechat目录下的文件。
    4. 处理datas/tmp目录下的文件
        4.1 根据账号名称,检查datas/wechat_operation_data/账号名称目录是否存在，如果不存在，则创建该目录。
        4.2 处理完之后的数据,更新到datas/wechat_operation_data/账号名称 目录下

    5. 公众号概念及元数据说明
        5.1 渠道:
            1) 推荐: 该渠道包括看一看、图文页底部相关推荐等场景
            2) 公众号消息: 公众号回话、公众号列表中的非看一看区域内容
"""

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
from tools import wechat_date_picker


class WechatDataFetcher:

    def __init__(self, begin_date=None, end_date=None):
        self.browser = None
        self.page = None
        self.begin_date = begin_date
        self.end_date = end_date
        self.tmp_data_dir = Path(config.root_dir) / 'tmp/data/wechat'
        self.account_name = None
        self.lock_file_name = "wechat_operation_data.lock"

    def prepare(self):
        """
        准备工作, 
        1. 初始化结束日期, 开始日期需要检查locker文件, 由于当前尚未登录，无法获知账号名称，因此无法获取开始日期。
            因此, 开始日期在登录后, 调用cal_begin_date方法计算。
        2. 清空tmp_data_dir目录下的文件
        """
        # 初始化结束日期范围
        if self.end_date is None:
            self.end_date = pendulum.now() - pendulum.duration(days=1)
        else:
            self.end_date = end_date

        # 确保self.tmp_data_dir存在
        if not self.tmp_data_dir.exists():
            self.tmp_data_dir.mkdir(parents=True)
        # 清空self.tmp_data_dir下所有文件
        for item in self.tmp_data_dir.iterdir():
            if item.is_file():
                item.unlink()
            elif item.is_dir():
                shutil.rmtree(item)

    def login(self, remember=True):               
        session_dir = Path(config.root_dir) / 'tmp/session/wechat/'
        if not session_dir.exists():
            session_dir.mkdir(parents=True)
        session_path = session_dir / 'wechat_session.json'

        # 定义通用的浏览器配置和headers
        user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3',
            'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:54.0) Gecko/20100101 Firefox/54.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36'
        ]

        p = sync_playwright().start()
        self.browser = p.chromium.launch(headless=False, downloads_path=self.tmp_data_dir)
        headers = {'User-Agent': random.choice(user_agents)}
        
        # 根据是否记住登录状态创建不同的上下文
        if remember and os.path.exists(session_path):
            context = self.browser.new_context(storage_state=session_path, extra_http_headers=headers)
        else:
            context = self.browser.new_context(extra_http_headers=headers)
            
        self.page = context.new_page()
        self.page.goto('https://mp.weixin.qq.com/')
        print('请扫码登录微信公众号后台...')
        self.page.wait_for_url('https://mp.weixin.qq.com/*')
        
        # 登录成功后保存session
        if remember:
            self.page.context.storage_state(path=session_path)

        # 等待导航栏加载完成
        self.page.wait_for_selector('#js_index_menu')
            
        # 模拟人类操作行为
        time.sleep(random.uniform(0.5, 3))
        scroll_distance = random.randint(100, 500)
        self.page.evaluate(f'window.scrollBy(0, {scroll_distance});')
                
    def fetch_account_name(self):
        """
        账号名称在导航栏最下方
        """
        self.page.wait_for_selector('div.account_box-body > span.acount_box-nickname')
        account_name = self.page.text_content('div.account_box-body > span.acount_box-nickname')
        self.account_name = account_name.strip()

    def cal_begin_date(self, begin_back_days=0):
        """
        计算开始日期，逻辑如下：
        1. 如果self.begin_date is not None, 则返回self.begin_date
        2. 使用Locker获取锁, 读取tmp/locks/wechat_operation_data.lock文件, 根据self.account_name, 获取value
        3. 如果value is not None, 则返回value
        4. 如果value is None, 则返回self.begin_date距离昨天30日前的日期

        @params begin_back_days 如果locker文件记录了上次执行的日期, 则返回距离该日期begin_back_days日前的日期
        """
        if self.begin_date is not None:
            return self.begin_date
        # 读取tmp/locks/wechat_operation_data.lock文件, 根据self.account_name, 获取value
        with Locker(self.lock_file_name) as lock_file:
            data = lock_file.get()
            last_download_date = data.get(self.account_name, None)
        # 如果last_download_date is not None, 其格式为'2023-01-01', 转化为pendulum.date对象
        if last_download_date is not None:
            begin_date = pendulum.from_format(last_download_date, 'YYYY-MM-DD')
            # 如果begin_date为今天, 则退出程序, 提示用户不要重复下载
            if begin_date >= pendulum.now().start_of('day'):
                print('今天已经下载过数据了, 请不要重复下载')
                exit(1)
            return begin_date - pendulum.duration(days=begin_back_days)  
        # 如果last_download_date is None, 则返回self.begin_date距离昨天30日前的日期
        return pendulum.now() - pendulum.duration(days=30) 

    def download_all(self):
        self.prepare()
        self.login()
        self.fetch_account_name()
        traffic_path = self.download_traffic_data()
        article_7d_path = self.download_article_7d_data()
        article_detail_paths = self.download_article_detail_data()
        self.browser.close()

        # 清理，获取账号名称，更新locker文件，值为今天的日期，使用pendulum处理，格式为'2023-01-01'
        with Locker(self.lock_file_name) as lock_file:
            data = lock_file.get()
            data[self.account_name] = pendulum.now().format('YYYY-MM-DD')
            lock_file.set(data)

        return {
            "account_name": self.account_name,
            "download_paths":  [traffic_path, article_7d_path, article_detail_paths]
        }

    def download_traffic_data(self):
        self.page.click('text=数据分析')
        # 随机等待
        time.sleep(random.uniform(0.5, 3))
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

        # 根据self.cal_begin_date()和self.end_date来选择下载的日期范围
        wechat_date_picker.pick_date(self.cal_begin_date(), self.end_date, self.page, self.page.query_selector('//form[@class="mass_all_filter"]'))
        download_file_path = self.tmp_data_dir / 'traffic_data.xlsx'
        self._wait_for_download(lambda: first_download_link.click(), download_file_path)
        return download_file_path        

    def download_article_7d_data(self):
        # 检查“内容分析”是否可见
        if not self.page.is_visible('text=内容分析'):
            self.page.click('text=数据分析')
            time.sleep(random.uniform(0.5, 3))
        self.page.click('text=内容分析')
        # 随机等待
        time.sleep(random.uniform(0.5, 3))
        # 直接点击"已通知内容"的a标签
        self.page.click('a:has-text("已通知内容")')
        # 等待“下载明细数据”a标签可见
        self.page.wait_for_selector('a:has-text("下载数据明细")', state='visible')

        # 更精确地定位日期选择器的父元素，先找到包含日期选择器的面板
        date_picker_parent = self.page.query_selector('div.weui-desktop-panel__bd form')
        wechat_date_picker.pick_date(self.cal_begin_date(7), self.end_date, self.page, date_picker_parent)

        download_file_path = self.tmp_data_dir / 'article_7d_data.xlsx'
        self._wait_for_download(lambda: self.page.click('a:has-text("下载数据明细")'), download_file_path)
        return download_file_path

    def download_article_detail_data(self):
        # 检查“内容分析”是否可见
        if not self.page.is_visible('text=内容分析'):
            self.page.click('text=数据分析')
            time.sleep(random.uniform(0.5, 3))
        self.page.click('text=内容分析')
        # 随机等待
        time.sleep(random.uniform(0.5, 3))
        # 直接点击"已通知内容"的a标签
        self.page.click('a:has-text("已通知内容")')
        # 确保class="weui-desktop-table"的表格加载
        self.page.wait_for_selector('table.weui-desktop-table', state='visible')

        # 更精确地定位日期选择器的父元素，先找到包含日期选择器的面板
        date_picker_parent = self.page.query_selector('div.weui-desktop-panel__bd form')
        wechat_date_picker.pick_date(self.cal_begin_date(30), self.end_date, self.page, date_picker_parent)
        
        download_file_paths = []
        def process_articles():
            """处理文章表格数据，包括等待表格加载和处理每行数据"""
            # 等待表格加载完成
            self.page.wait_for_selector('table.weui-desktop-table', state='attached')
            time.sleep(1)  # 额外等待1秒确保完全加载
            
            table = self.page.query_selector('table.weui-desktop-table')
            rows = table.query_selector_all('tbody tr')  # 只获取tbody中的tr元素
            
            for row in rows:
                a_tag = row.query_selector('a:has-text("详情")')
                if not a_tag:
                    continue

                while not a_tag.is_visible():
                    self.page.evaluate('window.scrollBy(0, 100);')
                    time.sleep(0.5)

                # 随机等待
                time.sleep(random.uniform(0.5, 2))

                # 打开详情链接，会新开标签页
                with self.page.context.expect_page() as new_page_info:
                    a_tag.click()
                new_page = new_page_info.value
                # 等待新页面加载完成
                new_page.wait_for_load_state()
                
                try:
                    # 在新页面中等待下载链接可见
                    new_page.wait_for_selector('a:has-text("下载数据明细")', state='visible')
                    # 获取文章标题
                    title = new_page.text_content('//div[contains(@class, "top_title")]//span[contains(@class, "weui-desktop-breadcrum")]')
                    # 随机等待
                    time.sleep(random.uniform(1, 5))
                    # 在新页面中点击下载
                    download_file_path = self.tmp_data_dir / f'{title}.xlsx'
                    self._wait_for_download(lambda: new_page.click('a:has-text("下载数据明细")'), download_file_path, new_page)
                    download_file_paths.append(download_file_path)

                    # 模拟人类操作行为
                    time.sleep(random.uniform(0.5, 3))
                    scroll_distance = random.randint(100, 500)
                    new_page.evaluate(f'window.scrollBy(0, {scroll_distance});')
                finally:
                    # 关闭新标签页并切换回原页面
                    new_page.close()
                    self.page.bring_to_front()

        # 执行文章处理
        process_articles()

        # 处理分页，检查“下一页”按钮是否存在，且可见，则点击下一页，然后滚动到顶部，处理文章
        while self.page.is_visible('a:has-text("下一页")'):
            self.page.click('a:has-text("下一页")')
            time.sleep(random.uniform(1, 3))
            # 滚动到顶部
            self.page.evaluate('window.scrollTo(0, 0);')
            # 处理文章
            process_articles()

        return download_file_paths

        
    def _wait_for_download(self, click_action, path=None, page=None, timeout=60):
        if page is None:
            page = self.page
        with page.expect_download() as download_info:
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
            time.sleep(1)
