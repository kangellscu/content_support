# 项目初始化指南

## 1. 执行初始化脚本
执行`init.sh`脚本完成项目初始化，该脚本会安装项目所需的所有依赖。使用以下命令执行脚本：
```bash
sh init.sh
```
这样，项目就完成了初始化，可以开始开发工作了。

## 2. 配置环境变量
在项目根目录下创建`.env`文件，根据`.env.example`文件的内容填写环境变量。


## 3. 如何执行任务
在项目根目录下执行以下命令：
```bash
poetry run command_line_tool.py [task]
```
例如，要执行`task1`任务，可以执行以下命令：
```bash
poetry run command_line_tool.py task1
``` 
查看帮助信息：
```bash
poetry run command_line_tool.py -h
```