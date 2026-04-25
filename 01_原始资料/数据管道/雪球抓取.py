#!/usr/bin/env python3
"""
雪球罗洄头发言抓取脚本
使用浏览器自动化抓取最新发言
"""
import os
import json
import sys
from datetime import datetime

# 项目路径
PROJECT_PATH = "/Users/humiles/OpenClaw项目/莫大韭菜"
DATA_DIR = f"{PROJECT_PATH}/01_原始资料/雪球罗洄头/发言"

def main():
    today = datetime.now().strftime("%Y-%m-%d")
    output_file = f"{DATA_DIR}/{today}_发言.json"
    
    print(f"📌 需要浏览器自动化抓取")
    print(f"   请在 OpenClaw 中执行以下步骤：")
    print(f"   1. 打开浏览器访问 https://xueqiu.com/u/2632831661")
    print(f"   2. 截图或复制最新发言内容")
    print(f"   3. 保存为 {output_file}")
    print()
    print("💡 或者手动访问雪球抓取后放入发言文件夹")

if __name__ == "__main__":
    main()
