# 命令行调用工具，支持命令参数解析，根据参数读取脚本路由文件，执行不同的业务逻辑
import sys
import importlib

if __name__ == '__main__':
    # 解析命令行参数
    if len(sys.argv) < 2:
        print('请提供脚本路由名称作为参数。')
        sys.exit(1)
    script_route_name = sys.argv[1]
    
    try:
        # 导入脚本路由模块
        script_route_module = importlib.import_module('script_routes')
        
        # 执行相应的业务逻辑
        if hasattr(script_route_module, script_route_name):
            func = getattr(script_route_module, script_route_name)
            func()
        else:
            print(f'未找到名为 {script_route_name} 的脚本路由。')
    except ImportError:
        print('无法导入脚本路由模块。')
    except Exception as e:
        print(f'执行脚本路由时出错: {e}')