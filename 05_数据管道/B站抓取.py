#!/usr/bin/env python3
"""
B站评论抓取脚本
使用浏览器自动化抓取最新评论
"""
import os
import json
from datetime import datetime

# 项目路径
PROJECT_PATH = "/Users/humiles/OpenClaw项目/莫大韭菜"
DATA_DIR = f"{PROJECT_PATH}/01_原始资料/B站动态/评论树"

def main():
    today = datetime.now().strftime("%Y-%m-%d")
    print(f"📌 需要浏览器自动化抓取B站评论")
    print(f"   请在 OpenClaw 中执行抓取步骤")

if __name__ == "__main__":
    main()
