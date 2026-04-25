#!/usr/bin/env python3
"""
baostock 数据获取脚本
自动获取股票K线数据，更新本地CSV
"""

import os
import baostock as bl
import pandas as pd
from datetime import datetime

# 配置
HIST_DATA_DIR = "/Users/humiles/OpenClaw项目/莫大韭菜/02_市场数据/K线数据/A股"

# ============ 持仓股: (baostock代码, 本地代码, 名称) ============
STOCKS = [
    # 原有持仓
    ("sz.000762", "000762", "西藏矿业"),
    ("sz.002594", "002594", "比亚迪"),
    ("sz.002169", "002169", "智光电气"),
    ("sh.600343", "600343", "航天动力"),
    ("sh.688114", "688114", "华大智造"),
    ("sh.601020", "601020", "华钰矿业"),
    ("sz.002538", "002538", "司尔特"),
    ("sh.688559", "688559", "海目星"),
    ("sz.300034", "300034", "钢研高纳"),
    ("sh.688533", "688533", "上大股份"),
    ("sz.002549", "002549", "华特气体"),      # 氦气概念
    ("sh.603260", "603260", "曙光数创"),      # AI液冷
    # 2026-04-25 新增
    ("sh.688981", "688981", "中芯国际"),      # 半导体
    ("sh.688525", "688525", "佰维存储"),      # 存储芯片
    ("sz.002371", "002371", "北方华创"),      # 半导体设备
    ("sh.603986", "603986", "兆易创新"),      # 芯片设计
    ("sh.600231", "600231", "华虹公司"),      # 晶圆代工
    ("sh.603893", "603893", "瑞芯微"),        # 芯片设计
    ("sh.688795", "688795", "摩尔线程"),      # AI芯片/半导体
    ("sh.688802", "688802", "沐曦股份"),      # AI芯片
    ("sz.301308", "301308", "江波龙"),        # 存储模组
    # 2026-04-25 第二次新增
    ("sh.688235", "688235", "百济神州"),      # 创新药
    ("sh.600276", "600276", "恒瑞医药"),      # 创新药
]

# ============ 指数: (baostock代码, 本地代码, 名称) ============
INDICES = [
    # A股核心指数
    ("sh.000001", "000001", "上证指数"),
    ("sz.399001", "399001", "深证成指"),
    ("sz.399006", "399006", "创业板指"),
    ("sh.000688", "000688", "科创50"),
    ("bj.899050", "899050", "北证50"),
]

# ============ 板块ETF: (baostock代码, 本地代码, 名称) ============
SECTORS = [
    # 半导体
    ("sh.512760", "512760", "半导体ETF"),
    ("sh.159995", "159995", "券商ETF"),
    # 新能源
    ("sh.159825", "159825", "新能源车ETF"),
    ("sz.159808", "159808", "新能源ETF"),
    # 科技
    ("sh.515000", "515000", "科技ETF"),
    ("sh.159927", "159927", "科技龙头ETF"),
    # 消费
    ("sh.159928", "159928", "消费ETF"),
    ("sh.510300", "510300", "沪深300ETF"),
    # AI
    ("sh.159819", "159819", "AIETF"),
    # 资源/周期
    ("sh.159881", "159881", "资源ETF"),
    ("sh.160622", "160622", "周期ETF"),
]


def fetch(bs_code, start="2025-01-01", end=None):
    """获取K线"""
    if end is None:
        end = datetime.now().strftime("%Y-%m-%d")
    
    rs = bl.query_history_k_data_plus(bs_code,
        "date,open,high,low,close,volume,pctChg",
        start_date=start, end_date=end,
        frequency="d", adjustflag="2")
    
    data = []
    while rs.next():
        data.append(rs.get_row_data())
    
    if not data:
        return None
    
    return pd.DataFrame(data, columns=rs.fields)


def update_one(bs_code, local_code, name):
    """更新单个标的"""
    filepath = f"{HIST_DATA_DIR}/{local_code}.csv"
    print(f"{local_code} {name}", end=" ", flush=True)
    
    try:
        df_new = fetch(bs_code, "2025-01-01")
        if df_new is None or df_new.empty:
            print("无数据")
            return False
        
        # 标准化列名
        df_new.columns = ['date','open','high','low','close','volume','pct_change']
        
        if os.path.exists(filepath):
            df_old = pd.read_csv(filepath)
            old_date = pd.to_datetime(df_old['date']).max()
            new_date = pd.to_datetime(df_new['date']).max()
            
            if new_date > old_date:
                df_new = df_new[pd.to_datetime(df_new['date']) > old_date]
                df = pd.concat([df_old, df_new], ignore_index=True)
                print(f"{old_date.date()}→{new_date.date()}")
            else:
                print(f"无新数据")
                return False
        else:
            df = df_new
            print("新建")
        
        df.to_csv(filepath, index=False, encoding='utf-8')
        return True
        
    except Exception as e:
        print(f"错误: {e}")
        return False


def main():
    print(f"\n=== baostock 数据获取 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ===")
    
    lg = bl.login()
    if lg.error_code != '0':
        print(f"登录失败: {lg.error_msg}")
        return
    print(f"登录: {lg.error_msg}")
    
    count = 0
    
    print(f"\n--- 持仓股 ({len(STOCKS)}) ---")
    for bs, local, name in STOCKS:
        if update_one(bs, local, name):
            count += 1
    
    print(f"\n--- 指数 ({len(INDICES)}) ---")
    for bs, local, name in INDICES:
        if update_one(bs, local, name):
            count += 1
    
    print(f"\n--- 板块ETF ({len(SECTORS)}) ---")
    for bs, local, name in SECTORS:
        if update_one(bs, local, name):
            count += 1
    
    bl.logout()
    print(f"\n=== 完成: 更新 {count} 个 ===\n")


if __name__ == "__main__":
    main()
