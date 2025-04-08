# 项目初始化指南

## 1. 建立虚拟环境
首先，确保你已经安装了 `poetry`。如果还未安装，可以使用以下命令进行安装：
```bash
pip install poetry
```

由于 `pyproject.toml` 中设置了 `virtualenvs.in-project = true`，`poetry` 会在项目目录下创建虚拟环境。使用以下命令创建虚拟环境：
```bash
poetry install --no-root
```

## 2. 激活虚拟环境
使用以下命令激活刚刚创建的虚拟环境：
```bash
poetry shell
```

## 3. 安装依赖
使用 `poetry` 安装 `poetry.lock` 中的包：
```bash
poetry install
```

这样，项目就完成了初始化，可以开始开发工作了。