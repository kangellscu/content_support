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

    def login(self, remember=True):
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
        _pick_date(self.begin_date, self.end_date, self.page, date_picker_parent)

        self._wait_for_download(lambda: self.page.click('a:has-text("下载数据明细")'), self.tmp_data_dir / 'article_7d_data.xlsx')

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
        _pick_date(self.begin_date, self.end_date, self.page, date_picker_parent)
        
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
                    time.sleep(random.uniform(0.5, 3))
                    # 在新页面中点击下载
                    self._wait_for_download(lambda: new_page.click('a:has-text("下载数据明细")'), self.tmp_data_dir / f'{title}.xlsx', new_page)
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
        #self.fetcher.download_traffic_data()
        #self.fetcher.download_article_7d_data()
        self.fetcher.download_article_detail_data()
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