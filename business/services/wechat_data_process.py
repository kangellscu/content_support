import os
import pandas as pd
from pathlib import Path
from config import config
import pendulum


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