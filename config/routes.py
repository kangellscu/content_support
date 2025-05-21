routes = [
    ('wechat-file-2-pdf', 'business.services.wechat_content_crawler.run', '根据Excel文件中的链接爬取微信公众号文章，并保存为PDF文件。'),
    ('wx-data-fetch', 'business.apps.wechat_data_crawler.run', '调用wechat_data_crawler.py中的run方法'),
    ('wx-data-pub', 'business.apps.wechat_data_crawler.publish_wechat_data', '执行微信数据发布功能，接收account_name参数')
]