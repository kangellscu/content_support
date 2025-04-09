#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import asyncio
from playwright.async_api import async_playwright
import os
import re
import random
import pandas as pd
from config import config

"""
    此文件的主要功能是爬取微信公众号文章，并将文章内容保存为PDF文件。
    核心意图是从指定的Excel文件中读取文章链接，对这些链接对应的文章进行信息提取和保存操作。
    Excel文件：data/wechat_urls.xlsx
    保存目录：data/wechat_files/账号/日期_文章标题.pdf
"""

async def crawl_wechat_article(urls):
    """
    爬取微信公众号文章
    :param url: 文章链接
    :return: 文章信息字典
    """
    semaphore = asyncio.Semaphore(3)
    async def process_url(url):
        async with semaphore:
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=False)
                headers = {
                    'User-Agent': random.choice([
                        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3',
                        'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:54.0) Gecko/20100101 Firefox/54.0',
                        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36'
                    ])
                }
                page = await browser.new_page(extra_http_headers=headers)
                await page.goto(url, wait_until='load')
                await asyncio.sleep(random.uniform(1, 2))
                # 模拟滚动
                await page.evaluate('window.scrollBy(0, window.innerHeight/2);')
                await asyncio.sleep(random.uniform(1, 2))
                # 模拟点击
                try:
                    await page.click('body', force=True)
                except Exception:
                    pass
                await page.wait_for_selector('h1#activity-name')
                # 根据id获取文章标题
                title = await page.text_content('h1#activity-name')
                if not title:
                    raise ValueError("未找到文章标题")
                title = title.strip()
                    
                await page.wait_for_selector('#js_wx_follow_nickname')
                # 获取账号，从第二行开始查找
                account = (await page.evaluate("() => document.querySelector('#js_name').textContent")).strip()
                await page.wait_for_selector('#publish_time')
                # 获取发表日期
                # 根据id获取发布时间
                date_text = await page.evaluate("() => document.querySelector('#publish_time')?.textContent")
                if not date_text:
                    raise ValueError("未找到发表日期")
                date_match = re.search(r'\d{4}年\d{2}月\d{2}日', date_text)
                if date_match:
                    date = date_match.group(0)
                else:
                    raise ValueError("日期格式不正确")

                # 组织信息到字典中
                article_info = {
                    'title': title,
                    'account': account,
                    'date': date
                }

                # 检查data目录是否存在，若不存在则抛出异常
                data_dir = os.path.join(config.root_dir, 'data')
                if not os.path.exists(data_dir):
                    raise FileNotFoundError(f'目录 {data_dir} 不存在')

                # 创建保存PDF的目录
                pdf_dir = os.path.join(data_dir, f'wechat_files/{account}/')
                os.makedirs(pdf_dir, exist_ok=True)

                # 生成PDF文件名
                pdf_filename = f'{date}_{title}.pdf'
                pdf_path = os.path.join(pdf_dir, pdf_filename)

                # 缓慢滚动页面到最后
                scroll_height = await page.evaluate('document.body.scrollHeight')
                for i in range(0, scroll_height, 100):
                    await page.evaluate(f'window.scrollTo(0, {i});')
                    await asyncio.sleep(random.uniform(0.1, 0.3))

                # 等待同时满足img标签且class包含rich_pages和wxw-img的元素加载完成
                await page.wait_for_selector('img.rich_pages.wxw-img')

                # 保存文章为PDF
                await page.pdf(path=pdf_path)

                await browser.close()
                return article_info
    tasks = [process_url(url) for url in urls]
    results = await asyncio.gather(*tasks)
    return results


def run():
    """
    爬取微信公众号文章
    :return: 文章信息字典
    """
    # 读取Excel文件中的链接
    data_dir = os.path.join(config.root_dir, 'data')
    excel_file_path = os.path.join(data_dir, 'wechat_urls.xlsx')
    try:
        # 直接读取Excel文件
        df = pd.read_excel(excel_file_path)
        # 提取文章链接
        urls = df['文章链接'].tolist()
    except FileNotFoundError:
        print(f'未找到文件 {excel_file_path}')
        urls = []
    except KeyError:
        print('Excel文件中未找到指定的链接列名')
        urls = []

    result = asyncio.run(crawl_wechat_article(urls))
    return result



if __name__ == '__main__':
    result = run()
    print(result)