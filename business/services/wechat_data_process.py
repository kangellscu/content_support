import pandas as pd
from pathlib import Path
from config import config


class WechatDataAnalyzer:
    """
    微信运营数据处理类，用于处理微信运营数据并进行分析。接收下载好的数据文件路径，更新本地数据文件
    主要功能包括：
    - 处理流量数据
        traffic数据是按日期组织的, 微信一旦生成, 该日的数据就会固定, 不需要更新, 因此只需要检查下载的文件和本地文件, 将
        下载文件中新的数据合并到本地文件中即可
        处理流程:
        1. 检查下载文件, 将渠道为"全部"的数据提取出来, 单独保存为traffic_summary, 剩余的部分保存为traffic 
        2. 检查本地文件traffic.csv是否存在, 如果不存在, 则traffic创建本地同名文件
        3. 检查本地文件traffic_summary.csv是否存在, 如果不存在, 则将traffic_summary创建本地同名文件
        4. 如果本地文件存在, 则读取本地文件和traffic, 将traffic中的数据合并到本地文件中, 合并时同时检查"日期","渠道"字段检查是否存在重复记录, 如果存在重复的"日期", "渠道"记录, 则保留traffic记录, 并将本地文件中重复的记录删除
        5. 如果本地文件存在, 则读取本地文件和traffic_summary, 将traffic_summary中的数据合并到本地文件中, 合并时同时检查"日期"字段检查是否存在重复记录, 如果存在重复的"日期"记录, 则保留traffic_summary记录, 并将本地文件中重复的记录删除
        6. 合并后的数据按照日期倒序排序, 并保存到本地文件中
    - 处理7天内文章数据
        7天内文章数据是按文章标题组织的, 文章发表7日内, 微信会更新文章数据, 因此需要更新本地文件
        处理流程:
        1. 检查下载文件, 保存为article_7d   
        1. 检查本地文件article_7d.csv是否存在, 如果不存在, 则将article_7d创建本地同名文件   
        2. 如果本地文件存在, 则读取本地文件和article_7d, 将article_7d的数据合并到本地文件中, 合并时同时检查"内容标题" 字段, 如果存在重复的"内容标题"记录, 则保留article_7d记录, 并将本地文件中重复的记录删除
        3. 合并后的数据按照日期倒序排序, 并保存到本地文件中
    - 处理文章详情数据
        文章详情数据是一个列表, 每个元素为一篇文章的下载文件路径, 文件名为"内容标题", 文件内容是一个复合表, 其中包含多个表格, 注意这些表格全部在同一个Worksheet中, 首先根据下面的规则把子表格提取出来:
        1. 子表之间用空行分隔, 子表第一行为表名, 第二行为字段名, 第三行开始为数据
        2. 子表格左右两侧有空列, 需要去掉
        提取成子表后，子表格处理流程如下:
        Step one: 首先需要将这些表格数据提取出来, 表格及其处理流程如下:
            1. 数据概况
                表名为"数据概况", 这个表格包含: 数据指标和数值两个字段, 将表格行列转置, 并将数据指标作为列名, 数值作为值, 存入detail_summary
            2. 阅读转化
                表名为"阅读转化", 这个表格包含: 数据指标和数值两个字段, 将表格行列转置, 并将数据指标作为列名, 数值作为值, 存入detail_read_convertion 
            3. 推荐转化
                表名为"推荐转化", 这个表格包含: 数据指标和数值两个字段, 将表格行列转置, 并将数据指标作为列名, 数值作为值, 存入detail_recommend_convertion
            4. 数据趋势明细
                表名为"数据趋势明细", 这个表格提取出来后, 存入detail_trend, 并将日期作为索引, 日期格式为"2024-01-01", 取出最小日期, 记为pub_date
            5. 性别分布
                表名为"性别分布", 这个表格去掉“占比"列, 存入detail_gender_distribution
            6. 年龄分布
                表名为"年龄分布", 这个表格去掉“占比"列, 存入detail_age_distribution
            7. 地域分布
                表名为"地域分布", 这个表格去掉“占比"列, 去掉"省份/直辖市"为全国的行, 存入detail_region_distribution
        Step two: 处理文章汇总数据
            1. 以列为方向, 合并detail_summary, detail_read_convertion, detail_recommend_convertion存入 article_detail
            2. 为article_detail添加一个字段, 字段名为"文章标题", 字段值为文章标题
            3. 为article_detail添加一个字段, 字段名为"发表日期", 字段值为pub_date
            4. 检查本地文件article_detail.csv是否存在, 如果不存在, 则直接将article_detail创建本地同名文件
            5. 如果本地文件存在, 则读取本地文件和article_detail, 根据"文章标题"将article_detail中的数据合并到本地文件中, 如果本地文件中已经存在该文章, 则更新数据
            6. 合并后的数据按照发表日期倒序排序, 并保存到本地文件中
        Step three: 处理趋势明细数据
            1. 为detail_trend添加一个字段, 字段名为"文章标题", 字段值为文章标题
            1. 检查本地文件article_trend_detail.csv是否存在, 如果不存在, 则直接将detail_trend创建本地文件
            2. 如果本地文件存在, 则读取本地文件和detail_trend, 根据"文章标题"和"日期"将detail_trend中的数据合并到本地文件中, 如果存在重复的"文章标题"和"日期"记录, 则保留detail_trend记录, 并将本地文件中重复的记录删除
            3. 合并后的数据按照日期倒序排序, 并保存到本地文件中
        Step four: 处理性别分布数据
            1. 为detail_gender_distribution添加一个字段, 字段名为"文章标题", 字段值为文章标题
            2. 检查本地文件article_gender_distribution.csv是否存在, 如果不存在, 则直接将detail_gender_distribution创建本地文件
            3. 如果本地文件存在, 则读取本地文件和detail_gender_distribution, 根据"文章标题"将detail_gender_distribution中的数据合并到本地文件中, 如果存在重复的"文章标题"记录, 则保留detail_gender_distribution记录, 并将本地文件中重复的记录删除
            4. 合并后的数据按照日期倒序排序, 并保存到本地文件中
        Step five: 处理年龄分布数据
            1. 为detail_age_distribution添加一个字段, 字段名为"文章标题", 字段值为文章标题
            2. 检查本地文件article_age_distribution.csv是否存在, 如果不存在, 则直接将detail_age_distribution创建本地文件
            3. 如果本地文件存在, 则读取本地文件和detail_age_distribution, 根据"文章标题"将detail_age_distribution中的数据合并到本地文件中, 如果存在重复的"文章标题"记录, 则保留detail_age_distribution记录, 并将本地文件中重复的记录删除
            4. 合并后的数据按照日期倒序排序, 并保存到本地文件中
        Step six: 处理地域分布数据
            1. 为detail_region_distribution添加一个字段, 字段名为"文章标题", 字段值为文章标题
            2. 检查本地文件article_region_distribution.csv是否存在, 如果不存在, 则直接将detail_region_distribution创建本地文件
            3. 如果本地文件存在, 则读取本地文件和detail_region_distribution, 根据"文章标题"将detail_region_distribution中的数据合并到本地文件中, 如果存在重复的"文章标题"记录, 则保留detail_region_distribution记录, 并将本地文件中重复的记录删除
            4. 合并后的数据按照日期倒序排序, 并保存到本地文件中
    - 发送处理后的数据
        将本地处理后的数据复制到指定目录下, 目录为: config.wechat_opt_data_dir.  复制过程中，如果文件存在, 则覆盖
    """
    def __init__(self, account_name, traffic_path=None, article_7d_path=None, article_detail_paths=None):
        self.account_name = account_name
        self.traffic_path = traffic_path
        self.article_7d_path = article_7d_path
        self.article_detail_paths = article_detail_paths or []
        self.send_dir = Path(config.wechat_opt_data_dir) / self.account_name
        self.data_dir = Path(config.root_dir) / 'datas/wechat_operation_data' / self.account_name
        # 检查self.send_dir 和 self.data_dir是否存在, 如果不存在, 则创建
        if not self.send_dir.exists():
            self.send_dir.mkdir(parents=True)
        if not self.data_dir.exists():
            self.data_dir.mkdir(parents=True)

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
            # 提取渠道为"全部"的数据
            traffic_summary = traffic_df[traffic_df['渠道'] == '全部']
            traffic = traffic_df[traffic_df['渠道'] != '全部']

            # 检查本地文件是否存在
            traffic_summary_path = self.data_dir / 'traffic_summary.csv'
            traffic_path = self.data_dir / 'traffic.csv'

            if traffic_summary_path.exists():
                local_traffic_summary = pd.read_csv(traffic_summary_path)
                # 合并时检查"日期"字段的重复记录，保留traffic_summary记录
                local_traffic_summary = local_traffic_summary[~local_traffic_summary['日期'].isin(traffic_summary['日期'])]
                traffic_summary = pd.concat([local_traffic_summary, traffic_summary], ignore_index=True)

            if traffic_path.exists():
                local_traffic = pd.read_csv(traffic_path)
                # 合并时检查"日期"和"渠道"字段的重复记录，保留traffic记录
                local_traffic = local_traffic[~local_traffic[['日期', '渠道']].apply(tuple, axis=1).isin(traffic[['日期', '渠道']].apply(tuple, axis=1))]
                traffic = pd.concat([local_traffic, traffic], ignore_index=True)

            # 合并后的数据按照日期倒序排序
            if not traffic_summary.empty:
                traffic_summary = traffic_summary.sort_values(by='日期', ascending=False)
            if not traffic.empty:
                traffic = traffic.sort_values(by='日期', ascending=False)

            # 保存到本地文件
            if not traffic_summary.empty:
                traffic_summary.to_csv(traffic_summary_path, index=False)
            if not traffic.empty:
                traffic.to_csv(traffic_path, index=False)

    def process_article_7d_data(self):
        """处理7天内文章数据"""
        if self.article_7d_path:
            # 读取下载文件
            article_7d = pd.read_excel(self.article_7d_path)
            
            # 检查本地文件是否存在
            article_7d_path = self.data_dir / 'article_7d.csv'
            
            if article_7d_path.exists():
                # 读取本地文件
                local_article_7d = pd.read_csv(article_7d_path)
                
                # 合并时检查“内容标题”字段的重复记录，保留article_7d记录
                local_article_7d = local_article_7d[~local_article_7d['内容标题'].isin(article_7d['内容标题'])]
                article_7d = pd.concat([local_article_7d, article_7d], ignore_index=True)
            
            # 合并后的数据按照日期倒序排序
            if not article_7d.empty:
                article_7d = article_7d.sort_values(by='发表时间', ascending=False)
            
            # 保存到本地文件
            if not article_7d.empty:
                article_7d.to_csv(article_7d_path, index=False)

    def process_article_detail_data(self):
        """处理文章详情数据"""
        for article_path in self.article_detail_paths:
            article_title = Path(article_path).stem
            # 读取文件
            xls = pd.ExcelFile(article_path)
            df = xls.parse(xls.sheet_names[0])        

            # 去除左右空列
            df = df.dropna(axis=1, how='all')
            
            # 提取子表
            table_start_indices = df[df.isnull().all(axis=1)].index.tolist()
            table_start_indices = [0] + [i + 1 for i in table_start_indices]
            table_end_indices = table_start_indices[1:] + [len(df)]
            
            detail_summary = None
            detail_read_convertion = None
            detail_recommend_convertion = None
            detail_trend = None
            pub_date = None
            detail_gender_distribution = None
            detail_age_distribution = None
            detail_region_distribution = None
            
            for start, end in zip(table_start_indices, table_end_indices):
                sub_table = df.iloc[start:end].dropna(how='all')
                if not sub_table.empty:
                    table_name = sub_table.iloc[0, 0]
                    sub_table = sub_table[2:].reset_index(drop=True)
                    sub_table.columns = df.iloc[start + 1]

                    # 删除空行空列
                    sub_table = sub_table.dropna(axis=0, how='all')
                    sub_table = sub_table.dropna(axis=1, how='all')
                    
                    if table_name == '数据概况':
                        detail_summary = sub_table.transpose()
                        detail_summary.columns = detail_summary.iloc[0]
                        detail_summary = detail_summary[1:].reset_index(drop=True)
                    elif table_name == '阅读转化':
                        detail_read_convertion = sub_table.transpose()
                        detail_read_convertion.columns = detail_read_convertion.iloc[0]
                        detail_read_convertion = detail_read_convertion[1:].reset_index(drop=True)
                    elif table_name == '推荐转化':
                        detail_recommend_convertion = sub_table.transpose()
                        detail_recommend_convertion.columns = detail_recommend_convertion.iloc[0]
                        detail_recommend_convertion = detail_recommend_convertion[1:].reset_index(drop=True)
                    elif table_name == '数据趋势明细':
                        detail_trend = sub_table
                        # 从 detail_trend 中提取 '日期' 列，转换为 datetime 类型，然后计算最小值
                        pub_date = pd.to_datetime(detail_trend['日期'], format='%Y-%m-%d').min()
                    elif table_name == '性别分布':
                        detail_gender_distribution = sub_table.drop('占比', axis=1)
                    elif table_name == '年龄分布':
                        detail_age_distribution = sub_table.drop('占比', axis=1)
                    elif table_name == '地域分布':
                        detail_region_distribution = sub_table.drop('占比', axis=1)
                        detail_region_distribution = detail_region_distribution[detail_region_distribution['省份/直辖市'] != '全国']
            
            # 处理文章汇总数据
            article_detail = pd.concat([detail_summary, detail_read_convertion, detail_recommend_convertion], axis=1)
            article_detail['文章标题'] = article_title
            # pub_date为datetime类型, 转换为字符串
            article_detail['发表日期'] = pub_date.strftime('%Y-%m-%d')
            
            article_detail_path = self.data_dir / 'article_detail.csv'
            if article_detail_path.exists():
                local_article_detail = pd.read_csv(article_detail_path)
                local_article_detail = local_article_detail[local_article_detail['文章标题'] != article_title]
                article_detail = pd.concat([local_article_detail, article_detail], ignore_index=True)
            if not article_detail.empty:
                article_detail = article_detail.sort_values(by='发表日期', ascending=False)
                article_detail.to_csv(article_detail_path, index=False)
            
            # 处理趋势明细数据
            if detail_trend is not None:
                detail_trend['文章标题'] = article_title
                article_trend_detail_path = self.data_dir / 'article_trend_detail.csv'
                if article_trend_detail_path.exists():
                    local_article_trend_detail = pd.read_csv(article_trend_detail_path)
                    local_article_trend_detail = local_article_trend_detail[~((local_article_trend_detail['文章标题'] == article_title) & (local_article_trend_detail['日期'].isin(detail_trend['日期'])))]
                    detail_trend = pd.concat([local_article_trend_detail, detail_trend], ignore_index=True)
                if not detail_trend.empty:
                    detail_trend = detail_trend.sort_values(by='日期', ascending=False)
                    detail_trend.to_csv(article_trend_detail_path, index=False)
            
            # 处理性别分布数据
            if detail_gender_distribution is not None:
                detail_gender_distribution['文章标题'] = article_title
                article_gender_distribution_path = self.data_dir / 'article_gender_distribution.csv'
                if article_gender_distribution_path.exists():
                    local_article_gender_distribution = pd.read_csv(article_gender_distribution_path)
                    local_article_gender_distribution = local_article_gender_distribution[local_article_gender_distribution['文章标题'] != article_title]
                    detail_gender_distribution = pd.concat([local_article_gender_distribution, detail_gender_distribution], ignore_index=True)
                if not detail_gender_distribution.empty:
                    detail_gender_distribution = detail_gender_distribution.sort_values(by='文章标题', ascending=False)
                    detail_gender_distribution.to_csv(article_gender_distribution_path, index=False)
            
            # 处理年龄分布数据
            if detail_age_distribution is not None:
                detail_age_distribution['文章标题'] = article_title
                article_age_distribution_path = self.data_dir / 'article_age_distribution.csv'
                if article_age_distribution_path.exists():
                    local_article_age_distribution = pd.read_csv(article_age_distribution_path)
                    local_article_age_distribution = local_article_age_distribution[local_article_age_distribution['文章标题'] != article_title]
                    detail_age_distribution = pd.concat([local_article_age_distribution, detail_age_distribution], ignore_index=True)
                if not detail_age_distribution.empty:
                    detail_age_distribution = detail_age_distribution.sort_values(by='文章标题', ascending=False)
                    detail_age_distribution.to_csv(article_age_distribution_path, index=False)
            
            # 处理地域分布数据
            if detail_region_distribution is not None:
                detail_region_distribution['文章标题'] = article_title
                article_region_distribution_path = self.data_dir / 'article_region_distribution.csv'
                if article_region_distribution_path.exists():
                    local_article_region_distribution = pd.read_csv(article_region_distribution_path)
                    local_article_region_distribution = local_article_region_distribution[local_article_region_distribution['文章标题'] != article_title]
                    detail_region_distribution = pd.concat([local_article_region_distribution, detail_region_distribution], ignore_index=True)
                if not detail_region_distribution.empty:
                    detail_region_distribution = detail_region_distribution.sort_values(by='文章标题', ascending=False)
                    detail_region_distribution.to_csv(article_region_distribution_path, index=False)


    def send_processed_data(self):
        # 发送处理后的数据
        pass