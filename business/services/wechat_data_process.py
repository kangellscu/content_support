import os
import pandas as pd
from pathlib import Path
from config import config
import pendulum


class WechatDataAnalyzer:
    """
    微信运营数据处理类，用于处理微信运营数据并进行分析。接收下载好的数据文件路径，更新本地数据文件
    主要功能包括：
    - 处理流量数据
        traffic数据是按日期组织的, 微信一旦生成, 该日的数据就会固定, 不需要更新, 因此只需要检查下载的文件和本地文件, 将
        下载文件中新的数据合并到本地文件中即可
        处理流程:
        1. 检查下载文件, 将渠道为"全部"的数据提取出来, 单独保存为traffic_summary, 剩余的部分保存为traffic 
        1. 检查本地文件traffic.csv是否存在, 如果不存在, 则将traffic_summary, traffic创建本地同名文件
        2. 如果本地文件traffic_summary.csv存在, 则读取本地文件, 将traffic_summary和traffic合并到本地文件中
        3. 合并后的数据按照日期倒序排序, 并保存到本地文件中
    - 处理7天内文章数据
        7天内文章数据是按文章标题组织的, 文章发表7日内, 微信会更新文章数据, 因此需要更新本地文件
        处理流程:
        1. 检查本地文件article_7d.csv是否存在, 如果不存在, 则直接将下载文件重命名为本地文件
        2. 如果本地文件存在, 则读取本地文件和下载文件, 根据文章标题将下载文件中的数据合并到本地文件中, 如果本地文件中已经存在该文章, 则更新数据
        3. 合并后的数据按照日期倒序排序, 并保存到本地文件中
    - 处理文章详情数据
        文章详情数据是按文章标题组织的, 每篇文章的下载文件是一个复合表, 其中包含多个表格,
        Step one: 首先需要将这些表格数据提取出来, 表格及其处理流程如下:
            1. 数据概况
                这个表格包含: 数据指标和数值两个字段, 将表格行列转置, 并将数据指标作为列名, 数值作为值, 存入detail_summary
            2. 阅读转化
                这个表格包含: 数据指标和数值两个字段, 将表格行列转置, 并将数据指标作为列名, 数值作为值, 存入detail_read_convertion 
            3. 推荐转化
                这个表格包含: 数据指标和数值两个字段, 将表格行列转置, 并将数据指标作为列名, 数值作为值, 存入detail_recommend_convertion
            4. 数据趋势明细
                这个表格提取出来后, 存入detail_trend, 并将日期作为索引, 日期格式为"2024-01-01", 取出最小日期, 记为pub_date
            5. 性别分布
                这个表格包含: 数据指标和数值两个字段, 将表格行列转置, 并将数据指标作为列名, 数值作为值, 去掉“占比"列, 存入detail_gender_distribution
            6. 年龄分布
                这个表格包含: 数据指标和数值两个字段, 将表格行列转置, 并将数据指标作为列名, 数值作为值, 去掉“占比"列, 存入detail_age_distribution
            7. 地域分布
                这个表格包含: 数据指标和数值两个字段, 将表格行列转置, 并将数据指标作为列名, 数值作为值, 去掉“占比"列, 存入detail_region_distribution
        Step two: 处理文章汇总数据
            1. 以列为方向, 合并detail_summary, detail_read_convertion, detail_recommend_convertion, detail_gender_distribution, detail_age_distribution, detail_region_distribution 存入 article_detail
            2. 为article_detail添加一个字段, 字段名为"文章标题", 字段值为文章标题
            3. 为article_detail添加一个字段, 字段名为"发表日期", 字段值为pub_date
            4. 检查本地文件article_detail.csv是否存在, 如果不存在, 则直接将article_detail创建本地同名文件
            5. 如果本地文件存在, 则读取本地文件和article_detail, 根据文章标题将article_detail中的数据合并到本地文件中, 如果本地文件中已经存在该文章, 则更新数据
            6. 合并后的数据按照发表日期倒序排序, 并保存到本地文件中
        Step three: 处理趋势明细数据
            1. 为detail_trend添加一个字段, 字段名为"文章标题", 字段值为文章标题
            1. 检查本地文件article_trend_detail.csv是否存在, 如果不存在, 则直接将detail_trend创建本地文件
            2. 如果本地文件存在, 则读取本地文件和detail_trend, 根据文章标题和日期将detail_trend中的数据合并到本地文件中, 如果本地文件中已经存在该记录, 则更新数据
            3. 合并后的数据按照日期倒序排序, 并保存到本地文件中
    - 发送处理后的数据
        将本地处理后的数据复制到指定目录下, 目录为: config.wechat_opt_data_dir.  复制过程中，如果文件存在, 则覆盖
    """
    def __init__(self, account_name, traffic_path=None, article_7d_path=None, article_detail_paths=None):
        self.account_name = account_name
        self.traffic_path = traffic_path
        self.article_7d_path = article_7d_path
        self.article_detail_paths = article_detail_paths or []
        
        # 确保数据目录存在
        self.data_dir = f'datas/wechat_operation_data/{self.account_name}'
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)

    def process_data(self):
        self.process_traffic_data()
        self.process_article_7d_data()
        self.process_article_detail_data()
        self.send_processed_data()

    def process_traffic_data(self):
        """
        处理流量数据
        """
        if self.traffic_path:
            traffic_df = pd.read_excel(self.traffic_path)
            # 这里可以添加具体的数据处理逻辑
            traffic_df.to_excel(os.path.join(self.data_dir, 'traffic.xlsx'), index=False)

    def process_article_7d_data(self):
        """
        处理7天内文章数据
        """
        if self.article_7d_path:
            article_7d_df = pd.read_excel(self.article_7d_path)
            # 这里可以添加具体的数据处理逻辑
            article_7d_df.to_excel(os.path.join(self.data_dir, 'article_7d.xlsx'), index=False)  

    def process_article_detail_data(self):
        """
        处理文章详情数据
        """
        if self.article_detail_paths:
            all_articles = []
            for path in self.article_detail_paths:
                article_df = pd.read_excel(path)
                all_articles.append(article_df)
            all_articles_df = pd.concat(all_articles, ignore_index=True)

    def send_processed_data(self):
        # 发送处理后的数据
        pass