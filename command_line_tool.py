# 命令行调用工具，支持命令参数解析，根据参数读取脚本路由文件，执行不同的业务逻辑
import sys
import importlib
import os
import argparse
from pathlib import Path
import trace
import traceback

if __name__ == '__main__':
    # 获取根目录并加入到sys.path
    root_dir = Path(os.path.dirname(os.path.abspath(__file__)))
    config_dir = root_dir / "config"
    sys.path.append(config_dir)

    # 解析命令行参数，获取要执行的任务列表
    # 创建参数解析器
    parser = argparse.ArgumentParser(description='命令行调用工具，支持执行不同的业务逻辑。')
    parser.add_argument('tasks', nargs='*', help='要执行的任务列表')
    parser.add_argument('-l', '--list', action='store_true', help='列出所有可用任务')
    args = parser.parse_args()
    # 获取要执行的任务列表
    try:
        # 导入config/routes.py模块
        routes_module = importlib.import_module('config.routes')
        routes = routes_module.routes
    except ImportError:
        print('无法导入config/routes.py模块。')
        sys.exit(1)
    task_list = args.tasks
    if args.list:
        print('所有可用任务:')
        for route in routes:
            print(f'{route[0]}: {route[2]}')
        sys.exit(0)
    
    try:
        for task in task_list:
            found = False
            for route in routes:
                if route[0] == task:
                    module_name, func_name = route[1].rsplit('.', 1)
                    print(module_name, func_name)
                    module = importlib.import_module(module_name)
                    func = getattr(module, func_name)
                    func()
                    found = True
                    break
            if not found:
                print(f'未找到名为 {task} 的任务。')
    except ImportError:
        print(f'无法导入 {module_name} 模块。')
        traceback.print_exc()
    except Exception as e:
        print(f'执行任务时出错: {e}')
        traceback.print_exc()