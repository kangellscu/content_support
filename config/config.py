from dotenv import load_dotenv
import os
# 这里可以定义项目配置项
# 示例配置
# CONFIG_ITEM = 'value'
load_dotenv()

root_dir = os.environ.get('ROOT_DIR')
parallel_num = int(os.environ.get('PARALLEL_NUM'))