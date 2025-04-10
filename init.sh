#!/bin/bash

# 从pyproject.toml中读取Python版本要求
PYTHON_REQUIRED=$(grep 'python =' pyproject.toml | cut -d'=' -f2 | tr -d ' "\n')
# 获取当前Python版本
PYTHON_CURRENT=$(python -c 'import sys; print("{}.{}.{}".format(sys.version_info.major, sys.version_info.minor, sys.version_info.micro))')
# 检查当前Python版本是否符合要求
echo "开始检查Python版本是否符合要求..."
if ! python -c "import packaging.version; assert packaging.version.parse('$PYTHON_CURRENT') >= packaging.version.parse('$PYTHON_REQUIRED'.lstrip('^'))" ; then
    echo "错误：当前Python版本 $PYTHON_CURRENT 不符合 pyproject.toml 中要求的 $PYTHON_REQUIRED 版本。" >&2
    exit 1
  else
    echo "Python版本符合要求，当前Python版本为： $PYTHON_CURRENT ，继续执行。"
  fi

# 确保已经安装了poetry
echo "开始检查Poetry是否已经安装..."
if ! command -v poetry &> /dev/null
  then
    echo "Poetry未安装，开始安装..."
    pip install poetry
    echo "Poetry安装完成。"
  else
    echo "Poetry已安装，无需执行。"
  fi

# 确保虚拟环境在项目目录中
poetry config virtualenvs.in-project true

# 检查虚拟环境是否已经建立
echo "开始检查虚拟环境是否已经建立..."
if [ ! -d ".venv" ]; then
    echo "虚拟环境未建立，开始建立..."
    poetry install --no-root
    echo "虚拟环境建立完成。"
  else
    echo "虚拟环境已建立，无需执行。"
  fi

# 创建datas目录，如果不存在
echo "开始检查datas目录是否存在..."
if [ ! -d "datas" ]; then
    echo "datas目录不存在，开始创建..."
    mkdir datas
    echo "datas目录创建完成。"
  else
    echo "datas目录已存在，无需执行。"
  fi

# 检查并安装Playwright浏览器
echo "开始检查并安装Playwright浏览器..."
if ! poetry run playwright --version &> /dev/null
  then
    echo "Playwright浏览器未安装，开始安装..."
    poetry run playwright install
    echo "Playwright浏览器安装完成。"
  else
    echo "Playwright浏览器已安装，版本号为：$(poetry run playwright --version)";
  fi
  echo "初始化已经完成"